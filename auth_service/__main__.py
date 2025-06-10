import argparse
import os
import sys
import logging
from auth_service.core.config import Config as auth_config

logging.basicConfig(level=logging.INFO)


def run_dev() -> int:
    import uvicorn

    uvicorn.run(
        "auth_service.fastapi_app:application",
        port=8000,
        log_level="info",
        reload=True,
        host="0.0.0.0",
    )
    return 0


def run_prod() -> int:
    import asyncio
    from auth_service.fastapi_app import application

    from hypercorn.config import Config
    from hypercorn.asyncio import serve

    config = Config()
    config.bind = ["0.0.0.0:443"]
    config.loglevel = "INFO"
    config.accesslog = "-"
    config.errorlog = "-"
    config.keyfile = auth_config().keyfile
    config.certfile = auth_config().certfile

    assert os.path.exists(config.keyfile), f"Key file {config.keyfile} does not exist"
    assert os.path.exists(
        config.certfile
    ), f"Cert file {config.certfile} does not exist"

    asyncio.run(serve(application, config))

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="auth_service", description="Auth service")
    parser.add_argument("-p", "--prod", action="store_true")

    args = parser.parse_args()

    if args.prod:
        return run_prod()

    return run_dev()


if __name__ == "__main__":
    sys.exit(main())
