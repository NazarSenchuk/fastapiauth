import time
from typing import Dict

import jwt
from decouple import config


JWT_SECRET = "MIIBOgIBAAJBAJ6oksacdp2wfTq3P4hvuZw3ll6vsMOITZ9WiFvZK7hHtGuXMdX1"
JWT_ALGORITHM ="HS256"


def token_response(token: str):
    return {
        "access_token": token
    }


def sign_jwt(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
