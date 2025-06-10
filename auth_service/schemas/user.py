import pydantic


class UserCreate(pydantic.BaseModel):
    email: str
    password: str


class UserGet(pydantic.BaseModel):
    id: int
    sub: str
    email: str

    class Config:
        from_attributes = True


class UserGetToken(pydantic.BaseModel):
    sub: str
    email: str
    exp: int

    class Config:
        from_attributes = True


class User(pydantic.BaseModel):
    id: int
    sub: str
    email: str
    hashed_password: str

    class Config:
        # orm_mode = True
        from_attributes = True
