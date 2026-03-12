from library.models import Base
from library.db import engine, SessionLocal

session = SessionLocal()

def create_tale():
    Base.metadata.create_all(bind=engine)


create_tale()