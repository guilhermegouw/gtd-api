from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from ..config import settings

router = APIRouter()

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/"
    + ".well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile",
        "prompt": "select_account",
    },
)


@router.get("/login/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get("userinfo")

    if user:
        request.session["user"] = dict(user)
        return JSONResponse(
            {
                "status": "success",
                "user": {
                    "email": user.get("email"),
                    "name": user.get("name"),
                    "picture": user.get("picture"),
                },
            }
        )
    return JSONResponse({"status": "error"}, status_code=400)
