from fastapi import Header, HTTPException

from app.core.secrets import get_token_map


def get_current_user(token: str | None = Header(None, alias="X-Auth-Token")) -> str:
    if token is None:
        raise HTTPException(status_code=401, detail="unauthorized")
    users = get_token_map()
    user = users.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="unauthorized")
    return user
