from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

db_uri = settings.SQLALCHEMY_DATABASE_URI

connect_args = {}
engine_kwargs = {"echo": False}

if db_uri.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    # MySQL / PostgreSQL cloud configurations (e.g. Aiven, AWS RDS)
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 3600
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(
    db_uri,
    connect_args=connect_args,
    **engine_kwargs,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
