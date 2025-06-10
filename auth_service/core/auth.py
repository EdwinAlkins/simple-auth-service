import jwt
from datetime import timezone, datetime
from fastapi.security import OAuth2PasswordBearer
from fnmatch import fnmatch

import auth_service.schemas.token as token_schema
import auth_service.core.config as config

SECRET_KEY = config.Config().secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = config.Config().access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_MINUTES = config.Config().refresh_token_expire_minutes

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="token")


def create_token(data: dict) -> str:
    """
    Create an token for the given data.

    Parameters:
        data: dict

    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decode the given token and return the payload.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def verify_token(token: str, credentials_exception) -> token_schema.TokenData:
    """
    Verify the given token and return the token data.

    Parameters:
        token: str
        credentials_exception: Exception

    Returns:
        token_schema.TokenData: The token data
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub: str = payload.get("sub")
        email: str = payload.get("email")
        if sub is None or email is None:
            raise credentials_exception
        token_data = token_schema.TokenData(sub=sub, email=email)
        return token_data
    except jwt.JWTError:
        raise credentials_exception


def is_allowed_redirect_url(redirect_url: str, allowed_patterns: tuple) -> bool:
    """
    Check if the given redirect URL is allowed.

    Parameters:
        redirect_url: str
        allowed_patterns: tuple

    Returns:
        bool: True if the redirect URL is allowed, False otherwise
    """
    for pattern in allowed_patterns:
        if fnmatch(redirect_url, pattern):
            return True
    return False


def compare_datetimes_aware(dt1: int | datetime, dt2: int | datetime) -> int:
    """
    Compare two datetime objects, making both offset-aware (UTC) if needed.
    Returns:
        -1 if dt1 < dt2
         0 if dt1 == dt2
         1 if dt1 > dt2
    """
    if isinstance(dt1, int):
        dt1 = datetime.fromtimestamp(dt1)
    if isinstance(dt2, int):
        dt2 = datetime.fromtimestamp(dt2)
    if dt1.tzinfo is None:
        dt1 = dt1.replace(tzinfo=timezone.utc)
    if dt2.tzinfo is None:
        dt2 = dt2.replace(tzinfo=timezone.utc)
    if dt1 < dt2:
        return -1
    elif dt1 > dt2:
        return 1
    else:
        return 0


def decode_token(token: str) -> dict:
    """
    Decode the given token and return the payload.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.JWTError:
        raise Exception("Invalid token")
