import asyncio
from aiohttp import web

from ...domain.utilities.verify_google_token import verify_google_token
from ...domain.utilities.authorize_user_and_get_info import authorize_user_and_get_info


def base_routes(server):
    routes = server.routes

    @routes.post("/breakpoints")
    async def post_breakpoints(request):
        info = authorize_user_and_get_info(request)

        if isinstance(info, web.Response):
            return info

        user_info = info.get("user_info", {})

        user_id = user_info.get("user_id")
        if not user_id:
            return web.json_response({"error": "No user id"}, status=401)

        json_data = await request.json()

        if "workflow_id" in json_data and ("node_ids" in json_data):
            workflow_with_breakpoints = server.toggle_breakpoints(
                user_id, json_data.get("workflow_id"), json_data.get("node_ids")
            )
            server.logger.info(workflow_with_breakpoints)

            return web.json_response(
                {
                    "user_id": user_id,
                    "workflow_id": json_data.get("workflow_id"),
                    "node_ids": json_data.get("node_ids"),
                }
            )
        else:
            return web.json_response(
                {"error": "no prompt", "node_errors": []}, status=400
            )

    @routes.post("/prompt")
    async def post_prompt(request):
        info = authorize_user_and_get_info(request)

        if isinstance(info, web.Response):
            return info

        user_info = info.get("user_info", {})

        user_id = user_info.get("user_id")
        if not user_id:
            return web.json_response({"error": "No user id"}, status=401)

        server.client_id = user_id

        json_data = await request.json()

        # on prompt handler
        json_data = server.trigger_on_prompt(json_data)

        if "prompt" in json_data:
            prompt = json_data["prompt"]

            server.current_workflow_id = json_data.get("workflow", {}).get("checksum")

            # use the service
            graph = server.graph_executor.prompt_to_graph(prompt)

            # TODO: validate prompt
            # valid = execution.validate_prompt(prompt)
            valid = True
            if valid:
                response = {
                    "prompt_id": json_data["promptId"],
                    "number": 1,
                    "node_errors": [],
                }

                # add the following to the server's run loop but don't block the request
                asyncio.create_task(
                    server.graph_executor.run_sequential(graph, response)
                )

                return web.json_response(response)
            else:
                server.logger.warning("invalid prompt: {}".format(valid))
                return web.json_response(
                    {"error": valid[1], "node_errors": valid[3]}, status=400
                )
        else:
            return web.json_response(
                {"error": "no prompt", "node_errors": []}, status=400
            )

    @routes.get("/extensions")
    async def get_extensions(request):
        info = authorize_user_and_get_info(request)

        if isinstance(info, web.Response):
            return info

        user_info = info.get("user_info", {})

        user_id = user_info.get("user_id")
        if not user_id:
            return web.json_response({"error": "No user id"}, status=401)

        # get list of loaded extensions from server
        extensions = server.extensions
        # compile response
        response_data = {}
        for ext_name, ext in extensions.items():
            ext_dict = {}
            ext_dict["name"] = ext.get("name", "")
            ext_dict["version"] = ext.get("version", "")
            ext_dict["description"] = ext.get("description", "")
            ext_dict["javascript"] = ext.get("javascript", "")
            ext_dict["javascript_class_name"] = ext.get("javascript_class_name", "")
            ext_dict["nodes"] = {}
            ext_dict["rules"] = {}

            for node_name, node in ext.get("nodes", {}).items():
                node_dict = {}
                node_dict["javascript_class_name"] = node.get(
                    "javascript_class_name", ""
                )
                node_dict["display_name"] = node.get("display_name", "")

                # from within the python class static values
                node_dict["category"] = node.get("python_class").CATEGORY
                node_dict["subcategory"] = node.get("python_class").SUBCATEGORY
                node_dict["description"] = node.get("python_class").DESCRIPTION

                node_dict["input"] = node.get("python_class").INPUT
                node_dict["output"] = node.get("python_class").OUTPUT

                ext_dict["nodes"][node_name] = node_dict

            for rule_name, rule in ext.get("rules", {}).items():
                rule_dict = {}
                rule_dict["javascript_class_name"] = rule.get(
                    "javascript_class_name", ""
                )
                rule_dict["display_name"] = rule.get("display_name", "")

                rule_dict["category"] = rule.get("python_class").CATEGORY
                rule_dict["subcategory"] = rule.get("python_class").SUBCATEGORY
                rule_dict["description"] = rule.get("python_class").DESCRIPTION

                rule_dict["parameters"] = rule.get("python_class").PARAMETERS

                ext_dict["rules"][rule_name] = rule_dict

            # add extension info to response
            response_data[ext_name] = ext_dict

        return web.json_response(response_data)

    @routes.get("/info")
    async def get_queue_info(request):
        info = authorize_user_and_get_info(request)

        if isinstance(info, web.Response):
            return info

        user_info = info.get("user_info", {})

        user_id = user_info.get("user_id")
        if not user_id:
            return web.json_response({"error": "No user id"}, status=401)

        return web.json_response(server.get_queue_info())

    @routes.get("/history")
    async def get_history(request):
        info = authorize_user_and_get_info(request)

        if isinstance(info, web.Response):
            return info

        user_info = info.get("user_info", {})

        user_id = user_info.get("user_id")
        if not user_id:
            return web.json_response({"error": "No user id"}, status=401)

        max_items = request.rel_url.query.get("max_items", None)
        if max_items is not None:
            max_items = int(max_items)
        return web.json_response(server.prompt_queue.get_history(max_items=max_items))

    @routes.get("/queue")
    async def get_queue(request):
        info = authorize_user_and_get_info(request)

        if isinstance(info, web.Response):
            return info

        user_info = info.get("user_info", {})

        user_id = user_info.get("user_id")
        if not user_id:
            return web.json_response({"error": "No user id"}, status=401)

        queue_info = {}
        current_queue = server.prompt_queue.get_current_queue()
        queue_info["queue_running"] = current_queue[0]
        queue_info["queue_pending"] = current_queue[1]
        return web.json_response(queue_info)

    ##########################################################
    # AUTHENTICATION
    ##########################################################

    @routes.post("/auth/sign-up/google")
    async def sign_up_google_auth(request):
        json_data = await request.json()

        token = json_data.get("token")

        info = {}

        try:
            info = verify_google_token(token)
            if info.get("error"):
                raise Exception(info.get("error"))
        except Exception as e:
            server.logger.error(e)
            return web.json_response({"error": str(e)}, status=400)

        return web.json_response({"user_info": info})

    @routes.post("/auth/sign-in/google")
    async def sign_in_google_auth(request):
        json_data = await request.json()

        token = json_data.get("token")

        info = {}

        try:
            info = verify_google_token(token)
            if info.get("error"):
                raise Exception(info.get("error"))
        except Exception as e:
            server.logger.error(e)
            return web.json_response({"error": str(e)}, status=400)

        return web.json_response({"user_info": info})
