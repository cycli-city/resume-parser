"""
Simple API key authentication.
 
Item 2 of the assignment ("FastAPI Authentication") is implemented here
as header-based API key auth via `X-API-Key`, applied as a dependency
on every protected route. Keys are configured through the API_KEYS
environment variable (comma-separated, no spaces), e.g.:
 
    export API_KEYS=devkey123,anotherkey456
 
If you need JWT/OAuth2 instead, swap the inside of `require_api_key`
for a token decode + validation step -- the route wiring (Depends)
stays identical.
"""
 
from __future__ import annotations
 
import os
 
from fastapi import Header, HTTPException, status
 
 
def _load_valid_keys() -> set[str]:
    raw = os.environ.get("API_KEYS", "")
    return {k.strip() for k in raw.split(",") if k.strip()}
 
 
def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    """FastAPI dependency: raises 401 if X-API-Key header is missing/invalid."""
    valid_keys = _load_valid_keys()
    if not valid_keys:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfigured: no API_KEYS set.",
        )
    if x_api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
    return x_api_key