from aiohttp import web, WSMsgType
from ...domain.utilities.authorize_user_and_get_info import authorize_user_and_get_info


def base_websocket(server):
    routes = server.routes

    @routes.get("/ws")
    async def websocket_handler(request):
        info = authorize_user_and_get_info(request)

        if isinstance(info, web.Response):
            return info

        user_info = info.get("user_info", {})

        user_id = user_info.get("user_id")
        if not user_id:
            return web.json_response({"error": "No user id"}, status=401)

        # sessions are scoped to the user
        session_id = user_id

        ws = web.WebSocketResponse(protocols=info.get("proto_list", []))

        await ws.prepare(request)

        # Reusing existing session, remove old
        server.sockets.pop(session_id, None)

        server.sockets[session_id] = ws

        try:
            # Send initial state to the new client
            await server.send(
                "status",
                {"status": server.get_queue_info(), "sid": session_id},
                session_id,
            )

            # On reconnect if we are the currently executing client send the current node
            if server.client_id == session_id and server.last_node_id is not None:
                await server.send(
                    "executing", {"node": server.last_node_id}, session_id
                )

            async for msg in ws:
                if msg.type == WSMsgType.ERROR:
                    server.logger.warning(
                        "ws connection closed with exception %s" % ws.exception()
                    )
        finally:
            server.sockets.pop(session_id, None)

        return ws
