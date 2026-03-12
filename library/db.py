from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, URL

from library.config import settings

engine = create_engine(
    url=URL.create(
        drivername="postgresql+psycopg2",
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        username=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
    )
)

SessionLocal = sessionmaker(bind=engine)
