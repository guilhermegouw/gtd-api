from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .routes import auth

app = FastAPI(
    title="GTD API", description="Getting Things Done API", version="0.1.0"
)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "GTD API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(auth.router, tags=["auth"])
