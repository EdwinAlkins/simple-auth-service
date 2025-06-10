from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from auth_service.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    sub = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class TokenSession(Base):
    __tablename__ = "token_sessions"

    id = Column(Integer, primary_key=True, index=True)
    uuid_refresh_token = Column(String, index=True)
    code = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, index=True)
    refresh_token = Column(String)
    access_token_expires_at = Column(DateTime)
    refresh_token_expires_at = Column(DateTime)
    created_at = Column(DateTime)
