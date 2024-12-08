from aiohttp import web

from .verify_google_token import verify_google_token

import os


def authorize_user_and_get_info(request):
    if not str(os.getenv("NEOSCAFFOLD_AUTH_ENABLED", "")).lower() == "true":
        return {"user_info": {"user_id": "neoscaffold_user"}, "proto_list": ["json"]}

    # if request is a websocket request, then we need to get the token from the query params
    ws_proto_header = request.headers.get("Sec-WebSocket-Protocol", "")

    authorization_header = ""
    authenticator_header = ""
    ws_proto_list = []

    if ws_proto_header:
        ws_proto_header = ws_proto_header.replace(" ", "")
        ws_proto_list = ws_proto_header.split(",")

        bearer_token = ws_proto_list[1]
        authenticator_header = ws_proto_list[2]
    else:
        authorization_header = request.headers.get("Authorization", "")
        if not authorization_header:
            return web.json_response({"error": "No token provided"}, status=401)

        bearer_token = (
            authorization_header.split(" ")[1] if authorization_header else None
        )

        authenticator_header = request.headers.get("Authenticator")

    if not bearer_token:
        return web.json_response({"error": "No token provided"}, status=401)

    if not authenticator_header:
        return web.json_response({"error": "No authenticator provided"}, status=401)

    authenticator = authenticator_header

    user_info = {}
    if authenticator == "google":
        user_info = verify_google_token(bearer_token)

        if user_info.get("error"):
            return web.json_response(user_info, status=401)
    else:
        return web.json_response({"error": "Unknown authenticator"}, status=401)

    return {"user_info": user_info, "proto_list": ws_proto_list}
