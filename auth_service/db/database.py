from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from auth_service.core.config import Config


# Création du moteur pour une base SQLite en mémoire
SQLALCHEMY_DATABASE_URL = f"sqlite:///{Config().database_path}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
