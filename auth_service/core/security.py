import re
import secrets


def validate_secret_key(key: str) -> tuple[bool, str | None]:
    """
    Validate the strength of the secret key according to several criteria.

    Args:
        key: The secret key to validate

    Returns:
        tuple[bool, str | None]: (is_valid, error_message)
    """
    if not key:
        return False, "The secret key cannot be empty"

    # Verification of the minimum length (512 bits = 64 characters in hex)
    if len(key) < 64:
        return False, "The secret key must be at least 64 characters (512 bits)"

    # Verification of the entropy (unique characters)
    if len(set(key)) < 32:
        return False, "The secret key must contain at least 32 unique characters"

    # Verification of the format (hexadecimal or base64)
    hex_pattern = re.compile(r"^[0-9a-fA-F]+$")
    base64_pattern = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")

    if not (hex_pattern.match(key) or base64_pattern.match(key)):
        return False, "The secret key must be in hexadecimal or base64 format"

    return True, None


def generate_secure_key() -> str:
    """
    Generate a cryptographically secure secret key.

    Returns:
        str: A new secret key of 512 bits in hexadecimal
    """
    return secrets.token_hex(64)  # 64 bytes = 512 bits
