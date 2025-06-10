from sqlalchemy.orm import Session
import bcrypt
import uuid
from datetime import datetime, timezone
import logging

import auth_service.db.model.user as user_model
import auth_service.schemas.user as user_schema

logger = logging.getLogger("crud.user")


def get_user(db: Session, user_id: int) -> user_model.User | None:
    return db.query(user_model.User).filter(user_model.User.id == user_id).one_or_none()


def get_user_by_email(db: Session, email: str) -> user_model.User | None:
    return (
        db.query(user_model.User).filter(user_model.User.email == email).one_or_none()
    )


def create_user(db: Session, user: user_schema.UserCreate) -> user_model.User:
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    hashed_password = hashed_password.decode("utf-8")
    db_user = user_model.User(
        sub=str(uuid.uuid4()), email=user.email, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def verify_password(plain_password: str, hashed_password: bytes | str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        (
            hashed_password
            if isinstance(hashed_password, bytes)
            else hashed_password.encode("utf-8")
        ),
    )


def get_token_session_by_code(db: Session, code: str) -> user_model.TokenSession | None:
    try:
        return (
            db.query(user_model.TokenSession)
            .filter(user_model.TokenSession.code == code)
            .filter(user_model.TokenSession.expires_at > datetime.now(timezone.utc))
            .first()
        )
    except Exception as e:
        logger.error(f"Error getting token session by code: {e}")
        return None


def create_token_session(
    db: Session, code: str, token: str, user_id: int, expires_at: datetime
) -> user_model.TokenSession:
    db_token_session = user_model.TokenSession(
        code=code, token=token, user_id=user_id, expires_at=expires_at
    )
    db.add(db_token_session)
    db.commit()
    db.refresh(db_token_session)
    return db_token_session


def delete_token_session_expired(db: Session) -> None:
    db.query(user_model.TokenSession).filter(
        user_model.TokenSession.expires_at < datetime.now(timezone.utc)
    ).delete()
    db.commit()
