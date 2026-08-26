from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base

if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine_kwargs = {"connect_args": connect_args}
    if settings.SQLALCHEMY_DATABASE_URI == "sqlite://":
        engine_kwargs["poolclass"] = StaticPool
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, **engine_kwargs)
else:
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
