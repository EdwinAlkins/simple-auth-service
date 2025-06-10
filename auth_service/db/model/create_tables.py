from auth_service.db.database import engine
from auth_service.db.model import user


def create_all() -> None:
    user.Base.metadata.create_all(bind=engine)
