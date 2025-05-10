#!/usr/bin/env python

import asyncio
from argparse import ArgumentParser, Namespace

from server import Server

__version__ = "0.0.1"


def parse_inputs(disabled=False) -> Namespace:
    """Parses the user program input"""
    parser = ArgumentParser(description="Add your arguments")

    if disabled:
        return parser.parse_args([])

    parser.add_argument(
        "--listen",
        type=str,
        default="127.0.0.1",
        metavar="IP",
        nargs="?",
        const="0.0.0.0",
        help="Specify the IP address to listen on (default: 127.0.0.1). If --listen is provided without an argument, it defaults to 0.0.0.0. (listens on all)",
    )
    parser.add_argument("--port", type=int, default=6166, help="Set the listen port.")
    parser.add_argument(
        "--tls-keyfile",
        type=str,
        help="Path to TLS (SSL) key file. Enables TLS, makes app accessible at https://... requires --tls-certfile to function",
    )
    parser.add_argument(
        "--tls-certfile",
        type=str,
        help="Path to TLS (SSL) certificate file. Enables TLS, makes app accessible at https://... requires --tls-keyfile to function",
    )
    parser.add_argument(
        "--enable-cors-header",
        type=str,
        default="*",
        metavar="ORIGIN",
        nargs="?",
        const="*",
        help="Enable CORS (Cross-Origin Resource Sharing) with optional origin or allow all with default '*'.",
    )
    parser.add_argument(
        "--max-upload-size",
        type=float,
        default=10000,
        help="Set the maximum upload size in MB. This prevents 413 Request Entity Too Large errors. Default is 100MB.",
    )

    parser.add_argument(
        "--extra-model-paths-config",
        type=str,
        default=None,
        metavar="PATH",
        nargs="+",
        action="append",
        help="Load one or more extra_model_paths.yaml files.",
    )
    parser.add_argument(
        "--output-directory", type=str, default=None, help="Set the output directory."
    )
    parser.add_argument(
        "--temp-directory",
        type=str,
        default=None,
        help="Set the temp directory (default is in the directory).",
    )
    parser.add_argument(
        "--input-directory", type=str, default=None, help="Set the input directory."
    )

    parser.add_argument(
        "--auto-launch",
        action="store_true",
        help="Automatically launch in the default browser.",
    )
    parser.add_argument(
        "--disable-auto-launch",
        action="store_true",
        help="Disable auto launching the browser.",
    )

    parser.add_argument(
        "--dont-print-server", action="store_true", help="Don't print server output."
    )
    parser.add_argument(
        "--quick-test-for-ci", action="store_true", help="Quick test for CI."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enables more debug prints."
    )

    parser.add_argument(
        "--enable-smart-cache",
        action="store_true",
        default=False,
        help="Enables smart cache each node output caches with inputs and parameters.",
    )
    parser.add_argument(
        "--inspection-delay",
        type=float,
        default=0,
        help="Set the inspection delay for each node to make it easier to see the output of the node in the UI in seconds.",
    )

    return parser.parse_args()


async def run(server, address="", port=6166, verbose=True, call_on_start=None):
    await asyncio.gather(
        server.start(address, port, verbose, call_on_start), server.publish_loop()
    )


def main() -> int:
    """Build many objects to process into our algolia database"""
    args = parse_inputs()
    print(args.port)

    # create event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # create server
    server = Server(loop=loop, args=args)

    # load extensions
    server = server.load_extensions()

    # add routes
    server.add_routes()

    call_on_start = None
    if args.auto_launch:

        def startup_server(scheme, address, port):
            import webbrowser

            webbrowser.open(f"{scheme}://{address}:{port}")

        call_on_start = startup_server
    try:
        loop.run_until_complete(
            run(
                server,
                address=args.listen,
                port=args.port,
                verbose=not args.dont_print_server,
                call_on_start=call_on_start,
            )
        )
    except KeyboardInterrupt:
        server.logger.info("\nStopped server")

    return 0


if __name__ == "__main__":
    main()
