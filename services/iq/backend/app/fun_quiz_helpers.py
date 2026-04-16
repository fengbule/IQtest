from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Header

from .security import decode_access_token


def get_current_admin(authorization: Annotated[str | None, Header()] = None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = authorization.split(" ", 1)[1]
    subject = decode_access_token(token)
    if not subject:
        raise HTTPException(status_code=401, detail="invalid token")
    return subject