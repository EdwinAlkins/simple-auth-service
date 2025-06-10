from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import datetime, timedelta, timezone
import uuid

import auth_service.core.auth as auth_core
import auth_service.crud.user as crud
from auth_service.db.database import get_db
import auth_service.schemas.user as user_schema
import auth_service.schemas.token as token_schema

router = APIRouter()


def get_token_session(
    db: Session, data: user_schema.UserCreate
) -> token_schema.TokenInfoWithCode:
    user = crud.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if not crud.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    code = str(uuid.uuid4())
    access_token_expires = datetime.now(timezone.utc) + timedelta(
        minutes=auth_core.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = auth_core.create_token(
        data={"sub": user.sub, "email": user.email, "exp": access_token_expires}
    )
    uuid_refresh_token = str(uuid.uuid4())
    refresh_token_expires = datetime.now(timezone.utc) + timedelta(
        minutes=auth_core.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    refresh_token = auth_core.create_token(
        data={"uuid": uuid_refresh_token, "exp": refresh_token_expires}
    )
    crud.create_token_session(
        db,
        code,
        uuid_refresh_token,
        access_token,
        refresh_token,
        user.id,
        access_token_expires,
        refresh_token_expires,
    )
    return token_schema.TokenInfoWithCode(
        code=code,
        access_token=access_token,
        token_type="bearer",
        access_token_expires_at=access_token_expires,
        refresh_token_expires_at=refresh_token_expires,
        refresh_token=refresh_token,
    )


def update_token_session(
    db: Session, uuid_refresh_token: str
) -> token_schema.TokenInfoWithCode:
    token_session = crud.get_token_session_by_uuid_refresh_token(db, uuid_refresh_token)
    if not token_session:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if (
        auth_core.compare_datetimes_aware(
            token_session.refresh_token_expires_at, datetime.now(timezone.utc)
        )
        < 0
    ):
        raise HTTPException(status_code=401, detail="Refresh token expired")
    user = crud.get_user_by_id(db, token_session.user_id)
    if not token_session:
        raise HTTPException(status_code=401, detail="Invalid token session")
    code = str(uuid.uuid4())
    access_token_expires = datetime.now(timezone.utc) + timedelta(
        minutes=auth_core.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = auth_core.create_token(
        data={"sub": user.sub, "email": user.email, "exp": access_token_expires}
    )
    new_uuid_refresh_token = str(uuid.uuid4())
    refresh_token_expires = datetime.now(timezone.utc) + timedelta(
        minutes=auth_core.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    refresh_token = auth_core.create_token(
        data={"uuid": new_uuid_refresh_token, "exp": refresh_token_expires}
    )
    crud.update_token_session(
        db,
        token_session.id,
        code,
        new_uuid_refresh_token,
        access_token,
        refresh_token,
        access_token_expires,
        refresh_token_expires,
    )
    return token_schema.TokenInfoWithCode(
        code=code,
        access_token=access_token,
        token_type="bearer",
        access_token_expires_at=access_token_expires,
        refresh_token_expires_at=refresh_token_expires,
        refresh_token=refresh_token,
    )


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> token_schema.TokenInfo:
    return get_token_session(
        db,
        user_schema.UserCreate(email=form_data.username, password=form_data.password),
    )


@router.post("/login")
async def login(
    data: user_schema.UserCreate,
    db: Session = Depends(get_db),
) -> token_schema.LoginCode:
    session = get_token_session(db, data)
    return token_schema.LoginCode(code=session.code)


@router.get("/exchange")
async def get_token(code: str, db: Session = Depends(get_db)) -> token_schema.TokenInfo:
    token_session = crud.get_token_session_by_code(db, code)
    if not token_session:
        raise HTTPException(status_code=401, detail="Invalid code")
    if (
        auth_core.compare_datetimes_aware(
            token_session.access_token_expires_at, datetime.now(timezone.utc)
        )
        < 0
    ):
        raise HTTPException(status_code=401, detail="Token expired")
    return token_schema.TokenInfo(
        access_token=token_session.token,
        token_type="bearer",
        access_token_expires_at=token_session.access_token_expires_at,
        refresh_token_expires_at=token_session.refresh_token_expires_at,
        refresh_token=token_session.refresh_token,
    )


@router.get("/me")
async def read_users_me(
    token: Annotated[str, Depends(auth_core.OAUTH2_SCHEME)],
) -> user_schema.UserGetToken:
    return user_schema.UserGetToken(**auth_core.decode_token(token))


@router.post("/register")
async def register_user(
    user: user_schema.UserCreate, db: Session = Depends(get_db)
) -> user_schema.UserGet:
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db, user)
    return user


@router.post("/refresh")
async def refresh_token(
    refresh_token: Annotated[str, Depends(auth_core.OAUTH2_SCHEME)],
    db: Session = Depends(get_db),
) -> token_schema.TokenInfo:
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    data_refresh_token = auth_core.decode_token(refresh_token)
    if not data_refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    # Get the uuid of the refresh token
    uuid_refresh_token: str | None = data_refresh_token.get("uuid")
    if not uuid_refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    # Check if the refresh token is expired
    if (
        not data_refresh_token.get("exp")
        or auth_core.compare_datetimes_aware(
            data_refresh_token.get("exp"), datetime.now(timezone.utc)
        )
        < 0
    ):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    return update_token_session(db, uuid_refresh_token)
