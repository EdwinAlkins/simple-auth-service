from datetime import datetime
import pydantic


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


class TokenData(pydantic.BaseModel):
    sub: str
    email: str | None = None


class TokenInfo(Token):
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime
    refresh_token: str

    class Config:
        from_attributes = True


class TokenInfoWithCode(TokenInfo):
    code: str


class LoginCode(pydantic.BaseModel):
    code: str

    class Config:
        from_attributes = True


class RefreshTokenData(pydantic.BaseModel):
    uuid: str
    expires_at: datetime
