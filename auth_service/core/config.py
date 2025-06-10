import os
import toml
from auth_service.core.security import validate_secret_key, generate_secure_key

DEFAULT_CONFIG_PATH = "config.toml"


def _load_config(config_path: str):
    """Load the config from the given path.

    Args:
        config_path (str): The path to the config file.

    Raises:
        FileNotFoundError: If the config file is not found.

    Returns:
        dict: The config as a dictionary.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    return toml.load(config_path)


class Config:
    """
    Configuration class for the application.
    """

    _instance = None

    __slots__ = [
        "secret_key",
        "access_token_expire_minutes",
        "refresh_token_expire_minutes",
        "database_path",
        "keyfile",
        "certfile",
        "config_toml",
    ]

    def __init__(self):
        # Get the secret key
        self.secret_key = os.getenv("SECRET_KEY")

        # If no secret key, generate a new one
        if not self.secret_key:
            self.secret_key = generate_secure_key()
            os.environ["SECRET_KEY"] = self.secret_key

        # Validation de la clé secrète
        is_valid, error_message = validate_secret_key(self.secret_key)
        if not is_valid:
            raise ValueError(f"SECRET_KEY invalide : {error_message}")

        # Configuration des autres paramètres
        self.database_path = os.getenv("DATABASE_PATH", "data/auth.db")
        if not os.path.exists(os.path.dirname(self.database_path)):
            os.makedirs(os.path.dirname(self.database_path))

        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
        )
        self.refresh_token_expire_minutes = int(
            os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7)  # 7 days by default
        )
        self.keyfile = os.getenv("KEYFILE", "certs/key.pem")
        self.certfile = os.getenv("CERTFILE", "certs/cert.pem")
        self.config_toml = _load_config(
            os.getenv("AUTH_SERVICE_CONFIG", DEFAULT_CONFIG_PATH)
        )

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def get_config():
        if Config._instance is None:
            Config._instance = Config()
        return Config._instance
