import importlib
import os
import ssl
import asyncio
import sys
import time
import aiohttp
import traceback
from aiohttp import web

import struct
import logging
from io import BytesIO

from PIL import Image, ImageOps
from ...domain.services.graph_executor import GraphExecutor
from ..apis.base_routes import base_routes
from ..apis.websocket_routes import base_websocket

# if python earlier than 3.12 import directly


class BinaryEventTypes:
    PREVIEW_IMAGE = 1
    UNENCODED_PREVIEW_IMAGE = 2


class Server:
    def __init__(self, loop, args, logger=None):
        self.loop = loop
        self.args = args

        # initialize message queue
        self.message_queue = asyncio.Queue()
        self.prompt_queue = asyncio.Queue()
        self.graph_executor = GraphExecutor(self)

        self.extensions = {}
        self.nodes = {}
        self.rules = {}

        self.middlewares = []

        if args.enable_cors_header:
            self.middlewares.append(
                self.create_cors_middleware(args.enable_cors_header)
            )
        self.ENABLE_SMART_CACHE = args.enable_smart_cache or False
        self.INSPECTION_DELAY = args.inspection_delay or 0

        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

        self.app = web.Application(middlewares=self.middlewares)

        self.sockets = {}
        self.sessions = {}
        self.last_node_id = None
        self.current_workflow_id = None
        self.client_id = None
        self.on_prompt_handlers = []

        routes = web.RouteTableDef()
        self.routes = routes

    def add_routes(self):
        base_routes(self)
        base_websocket(self)

        # add aiohttp routes to the routing table
        self.app.add_routes(self.routes)

    def get_queue_info(self):
        prompt_info = {}
        exec_info = {}
        exec_info["queue_remaining"] = self.prompt_queue.qsize()
        prompt_info["exec_info"] = exec_info
        return prompt_info

    def create_cors_middleware(self, allowed_origin: str):
        @web.middleware
        async def cors_middleware(request: web.Request, handler):
            if request.method == "OPTIONS":
                response = web.Response()
            else:
                response = await handler(request)

            response.headers["Access-Control-Allow-Origin"] = allowed_origin
            response.headers["Access-Control-Allow-Methods"] = (
                "POST, GET, DELETE, PUT, OPTIONS"
            )
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization, Authenticator, Sec-WebSocket-Protocol"
            )
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response

        return cors_middleware

    # sends image, bytes, or json data to the client
    async def send(self, event, data, sid=None):
        if event == BinaryEventTypes.UNENCODED_PREVIEW_IMAGE:
            await self.send_image(data, sid=sid)
        elif isinstance(data, (bytes, bytearray)):
            await self.send_bytes(event, data, sid)
        else:
            await self.send_json(event, data, sid)

    def encode_bytes(self, event, data):
        if not isinstance(event, int):
            raise RuntimeError(f"Binary event types must be integers, got {event}")

        # big-endian unsigned int packed
        packed = struct.pack(">I", event)
        message = bytearray(packed)
        message.extend(data)
        return message

    async def send_image(self, image_data, sid=None):
        image_type = image_data[0]
        image = image_data[1]
        max_size = image_data[2]
        if max_size is not None:
            if hasattr(Image, "Resampling"):
                resampling = Image.Resampling.BILINEAR
            else:
                resampling = Image.ANTIALIAS

            image = ImageOps.contain(image, (max_size, max_size), resampling)
        type_num = 1
        if image_type == "JPEG":
            type_num = 1
        elif image_type == "PNG":
            type_num = 2

        bytesIO = BytesIO()
        # big-endian unsigned int packed
        header = struct.pack(">I", type_num)
        bytesIO.write(header)
        image.save(bytesIO, format=image_type, quality=95, compress_level=1)
        preview_bytes = bytesIO.getvalue()
        await self.send_bytes(BinaryEventTypes.PREVIEW_IMAGE, preview_bytes, sid=sid)

    async def send_bytes(self, event, data, sid=None):
        message = self.encode_bytes(event, data)

        if sid is None:
            sockets = list(self.sockets.values())
            for ws in sockets:
                await self.try_send_socket(ws.send_bytes, message)
        elif sid in self.sockets:
            await self.try_send_socket(self.sockets[sid].send_bytes, message)

    async def send_json(self, event, data, sid=None):
        message = {"type": event, "data": data}

        if sid is None:
            sockets = list(self.sockets.values())
            for ws in sockets:
                await self.try_send_socket(ws.send_json, message)
        elif sid in self.sockets:
            await self.try_send_socket(self.sockets[sid].send_json, message)

    def send_sync(self, event, data, sid=None):
        self.loop.call_soon_threadsafe(
            self.message_queue.put_nowait, (event, data, sid)
        )

    def queue_updated(self):
        self.send_sync("status", {"status": self.get_queue_info()})

    async def publish_loop(self):
        while True:
            msg = await self.message_queue.get()
            await self.send(*msg)

    async def start(self, address, port, verbose=True, call_on_start=None):
        runner = web.AppRunner(self.app, access_log=None)
        await runner.setup()
        ssl_ctx = None
        scheme = "http"
        if self.args.tls_keyfile and self.args.tls_certfile:
            ssl_ctx = ssl.SSLContext(
                protocol=ssl.PROTOCOL_TLS_SERVER, verify_mode=ssl.CERT_NONE
            )
            ssl_ctx.load_cert_chain(
                certfile=self.args.tls_certfile, keyfile=self.args.tls_keyfile
            )
            scheme = "https"

        site = web.TCPSite(runner, address, port, ssl_context=ssl_ctx)
        await site.start()

        if verbose:
            self.logger.info("Starting server\n")
            self.logger.info(
                "To see the GUI go to: {}://{}:{}".format(scheme, address, port)
            )
        if call_on_start is not None:
            call_on_start(scheme, address, port)

    def get_or_create_session(self, client_id):
        if client_id not in self.sessions:
            self.sessions[client_id] = {}
        return self.sessions[client_id]

    def get_or_create_workflow(self, client_id, workflow_id):
        session = self.get_or_create_session(client_id)

        if workflow_id not in session:
            session[workflow_id] = {}

        return session[workflow_id]

    def import_extension_module(self, file_path):
        module_path = os.path.splitext(file_path)[0].replace(os.sep, ".")
        try:
            time_start = time.time()
            module = importlib.import_module(name=module_path)
            self.logger.warning(
                f"imported {module_path} in {time.time() - time_start:.4f} seconds"
            )
            return module
        except Exception as e:
            self.logger.error(f"Failed to execute startup-script: {file_path} / {e}")
        return False

    def load_extensions(self):
        """Load extensions"""
        server = self

        loading_start_timestamp = time.time()

        # load custom extensions
        server.load_custom_extensions()

        # load neos_ext packages
        server.load_neos_ext_packages()

        server.logger.warning(
            f"Loaded extensions in {time.time() - loading_start_timestamp:.4f} seconds"
        )
        return server

    def load_neos_ext_packages(self):
        server = self

        # for each package currently installed on the system
        for package in importlib.metadata.distributions():
            # if the package name starts with "neos-" and "neoscaffold" is in the keywords it's a NeoScaffold package
            if package.name.startswith(
                "neos-"
            ) and "neoscaffold" in package.metadata.get("Keywords", ""):
                time_start = time.time()
                module = importlib.import_module(
                    name=package.name.replace("-", "_") + ".extension"
                )
                server.load_extension_module(module=module)
                server.logger.warning(
                    f"imported {package.name} in {time.time() - time_start:.4f} seconds"
                )

    def load_custom_extensions(self):
        server = self
        path_to_current_file = os.path.realpath(__file__)

        # NOTE: this is the same as "...." (moving up 4 directories)
        path_to_root_folder = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(path_to_current_file)))
        )

        path_to_custom_extensions = os.path.join(
            path_to_root_folder, "custom_extensions"
        )

        sys.path.insert(0, path_to_custom_extensions)

        custom_extensions = [path_to_custom_extensions]

        for extension in custom_extensions:
            # filter things that are not directories of python modules
            possible_modules = [
                f
                for f in os.listdir(extension)
                if (
                    not f.endswith(".py")
                    and not f.startswith("__")
                    and not f.startswith(".")
                    and not os.path.isfile(f)
                    and not os.path.isfile(os.path.join(extension, f))
                )
            ]

            for possible_module in possible_modules:
                extension_script_path = os.path.join(
                    extension, possible_module, "extension.py"
                )
                if os.path.isfile(extension_script_path):
                    # custom_extensions.agents.extension
                    module = server.import_extension_module(
                        os.path.join(
                            "custom_extensions", possible_module, "extension.py"
                        )
                    )
                    server.load_extension_module(module=module)
                else:
                    server.logger.warning(
                        f"Skip {extension_script_path} module for custom extensions due to the lack of extension.py."
                    )

    def load_extension_module(self, module):
        server = self
        if (
            hasattr(module, "EXTENSION_MAPPINGS")
            and getattr(module, "EXTENSION_MAPPINGS") is not None
        ):
            # Extension
            server.extensions[module.EXTENSION_MAPPINGS.get("name")] = (
                module.EXTENSION_MAPPINGS
            )

            # Javascript
            extension_full_path = os.path.realpath(module.__file__)
            folder_path = os.path.dirname(extension_full_path)

            extension_script_path = os.path.join(folder_path, "web.js")
            if os.path.isfile(extension_script_path):
                with open(extension_script_path, "r") as f:
                    js_file_str = f.read()
                    server.extensions[module.EXTENSION_MAPPINGS.get("name")][
                        "javascript"
                    ] = js_file_str

            # Nodes
            for name, value in module.EXTENSION_MAPPINGS.get("nodes", {}).items():
                server.nodes[name] = value
            # Rules
            for name, value in module.EXTENSION_MAPPINGS.get("rules", {}).items():
                server.rules[name] = value

        else:
            server.logger.warning(
                f"Skip {module.__name__} module for custom extensions due to the lack of EXTENSION_MAPPINGS."
            )

    def toggle_breakpoints(self, client_id, workflow_id, node_ids=[]):
        workflow = self.get_or_create_workflow(client_id, workflow_id)

        if "breakpoints" not in workflow:
            workflow["breakpoints"] = {"last_modified": time.time(), "nodes": {}}

        if "nodes" not in workflow["breakpoints"]:
            workflow["breakpoints"]["nodes"] = {}

        for node_id in node_ids:
            if node_id in workflow["breakpoints"]["nodes"]:
                event = workflow["breakpoints"]["nodes"][node_id]
                event.clear()
                del workflow["breakpoints"]["nodes"][node_id]
            else:
                workflow["breakpoints"]["nodes"][node_id] = asyncio.Event()

        return workflow

    def step_through_breakpoints(self, client_id, workflow_id, node_ids=[]):
        workflow = self.get_or_create_workflow(client_id, workflow_id)

        if "breakpoints" not in workflow:
            workflow["breakpoints"] = {"last_modified": time.time(), "nodes": {}}

        if "nodes" not in workflow["breakpoints"]:
            workflow["breakpoints"]["nodes"] = {}

        for node_id in node_ids:
            if node_id in workflow["breakpoints"]["nodes"]:
                event = workflow["breakpoints"]["nodes"][node_id]
                if not event.is_set():
                    event.set()
                else:
                    event.clear()

        return workflow

    def add_on_prompt_handler(self, handler):
        self.on_prompt_handlers.append(handler)

    def trigger_on_prompt(self, json_data):
        for handler in self.on_prompt_handlers:
            try:
                json_data = handler(json_data)
            except Exception:
                self.logger.warning(
                    "[ERROR] An error occurred during the on_prompt_handler processing"
                )
                self.logger.warning(traceback.format_exc())

        return json_data

    async def try_send_socket(self, function, message):
        try:
            await function(message)
        except (
            aiohttp.ClientError,
            aiohttp.ClientPayloadError,
            ConnectionResetError,
        ) as err:
            self.logger.warning("send error: {}".format(err))
