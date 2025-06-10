from datetime import datetime
import pydantic


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


class TokenData(pydantic.BaseModel):
    sub: str
    email: str | None = None


class TokenInfo(Token):
    expires_in: datetime

    class Config:
        from_attributes = True


class LoginCode(pydantic.BaseModel):
    code: str

    class Config:
        from_attributes = True
