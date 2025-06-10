import os
import toml

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
        "database_path",
        "keyfile",
        "certfile",
        "config_toml",
    ]

    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY")
        if not self.secret_key:
            raise ValueError("SECRET_KEY is not set")
        self.database_path = os.getenv("DATABASE_PATH", "data/auth.db")
        if not os.path.exists(os.path.dirname(self.database_path)):
            os.makedirs(os.path.dirname(self.database_path))
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
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
