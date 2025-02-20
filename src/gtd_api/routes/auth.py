import logging

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import JSONResponse

from ..config import settings
from ..database import get_async_session
from ..models import User

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
async def auth_callback(
    request: Request, session: AsyncSession = Depends(get_async_session)
):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to get user info")

    try:
        stmt = select(User).where(User.email == user_info["email"])
        result = await session.execute(stmt)
        db_user = result.scalar_one_or_none()

        if db_user is None:
            db_user = User(
                email=user_info["email"],
                name=user_info["name"],
                picture=user_info["picture"],
            )
            session.add(db_user)
        else:
            db_user.name = user_info["name"]
            db_user.picture = user_info["picture"]

        await session.commit()

    except Exception as e:
        await session.rollback()
        logger.error(f"Database error during user operation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create user data",
        )

    request.session["user"] = {
        "id": db_user.id,
        "email": db_user.email,
        "name": db_user.name,
        "picture": db_user.picture,
    }

    return JSONResponse(
        {
            "status": "success",
            "user": {
                "id": db_user.id,
                "email": db_user.email,
                "name": db_user.name,
                "picture": db_user.picture,
            },
        }
    )
