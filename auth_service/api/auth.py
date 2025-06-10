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


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> token_schema.TokenInfo:
    user = crud.get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = datetime.now(timezone.utc) + timedelta(
        minutes=auth_core.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = auth_core.create_access_token(
        data={"sub": user.sub, "email": user.email, "exp": access_token_expires}
    )
    return token_schema.TokenInfo(
        access_token=access_token,
        token_type="bearer",
        expires_in=access_token_expires,
    )


@router.post("/login")
async def login(
    data: user_schema.UserCreate,
    db: Session = Depends(get_db),
) -> token_schema.LoginCode:
    code = str(uuid.uuid4())
    user = crud.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if not crud.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = datetime.now(timezone.utc) + timedelta(
        minutes=auth_core.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = auth_core.create_access_token(
        data={"sub": user.sub, "email": user.email, "exp": access_token_expires}
    )
    crud.create_token_session(
        db,
        code,
        access_token,
        user.id,
        access_token_expires,
    )
    return token_schema.LoginCode(code=code)


@router.get("/exchange")
async def get_token(code: str, db: Session = Depends(get_db)) -> token_schema.TokenInfo:
    token_session = crud.get_token_session_by_code(db, code)
    if not token_session:
        raise HTTPException(status_code=401, detail="Invalid code")
    if (
        auth_core.compare_datetimes_aware(
            token_session.expires_at, datetime.now(timezone.utc)
        )
        < 0
    ):
        raise HTTPException(status_code=401, detail="Token expired")
    return token_schema.TokenInfo(
        access_token=token_session.token,
        token_type="bearer",
        expires_in=token_session.expires_at,
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
