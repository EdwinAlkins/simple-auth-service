import os
import logging

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from apscheduler.schedulers.background import BackgroundScheduler

import auth_service.crud.user as crud
import auth_service.api.auth as auth_api
from auth_service.db.database import get_db
import auth_service.db.model.create_tables
import auth_service.core.auth as auth_core
import auth_service.core.config as config_util

logger = logging.getLogger(__name__)

application = FastAPI()
scheduler = BackgroundScheduler()

# Load the config
CONFIG = config_util.Config().config_toml

# Use the values from the config file
allow_origins = CONFIG.get("fastapi", {}).get(
    "allow_origins", ["http://localhost:8000/*"]
)
allow_headers = CONFIG.get("fastapi", {}).get("allow_headers", ["*"])
ALLOWED_REDIRECT_URLS = tuple(
    CONFIG.get("auth", {}).get("allowed_redirect_urls", ["http://localhost:8000/*"])
)

application.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=allow_headers,
)

application.include_router(auth_api.router)


@application.on_event("startup")
async def startup_event():
    logger.info("Starting up...")

    def local_delete_token_session_expired():
        db = next(get_db())
        crud.delete_token_session_expired(db)

    scheduler.add_job(local_delete_token_session_expired, "interval", minutes=10)
    scheduler.start()
    auth_service.db.model.create_tables.create_all()


@application.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()


@application.get("/")
async def root():
    return {"health": "ok"}


@application.get("/login", tags=["html"], response_class=HTMLResponse)
async def login(
    redirect_url: str | None = Query(
        None, description="The URL to redirect to after login"
    )
):
    if redirect_url and not auth_core.is_allowed_redirect_url(
        redirect_url, ALLOWED_REDIRECT_URLS
    ):
        raise HTTPException(status_code=400, detail="Invalid redirect URL")
    html_content = os.path.join(os.path.dirname(__file__), "static", "login.html")
    with open(html_content, "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)


@application.get("/register", tags=["html"], response_class=HTMLResponse)
async def register(
    redirect_url: str | None = Query(
        None, description="The URL to redirect to after registration"
    )
):
    html_content = os.path.join(os.path.dirname(__file__), "static", "register.html")
    with open(html_content, "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)


@application.get("/callback", tags=["html"], response_class=HTMLResponse)
async def callback(
    code: str = Query(..., description="The code to exchange for a token"),
):
    html_content = os.path.join(os.path.dirname(__file__), "static", "callback.html")
    with open(html_content, "r") as file:
        html_content = file.read()
    html_content = html_content.replace("{{ code }}", code)
    return HTMLResponse(content=html_content)


@application.get("/example", tags=["html"], response_class=HTMLResponse)
async def example():
    html_content = os.path.join(os.path.dirname(__file__), "static", "example.html")
    with open(html_content, "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)
