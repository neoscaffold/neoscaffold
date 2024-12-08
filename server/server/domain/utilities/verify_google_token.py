import os


def verify_google_token(token):
    client_id = os.getenv("GOOGLE_SIGN_IN_CLIENT_ID")
    from google.oauth2 import id_token
    from google.auth.transport import requests

    info = {"error": "Invalid token"}
    if token is not None:
        try:
            user_info = id_token.verify_oauth2_token(
                token, requests.Request(), client_id
            )
            info = {
                "user_id": user_info["sub"],
                "email": user_info["email"],
                "name": user_info["name"],
                "email_verified": user_info["email_verified"],
                "picture": user_info["picture"],
                "hosted_domain": user_info["hd"],
                "not_before": user_info["nbf"],
                "issued_at": user_info["iat"],
                "expiration": user_info["exp"],
                "jwt_id": user_info["jti"],
                "issuer": user_info["iss"],
            }
        except Exception as e:
            print(e)

            info = {"error": str(e)}

            return info
    return info
