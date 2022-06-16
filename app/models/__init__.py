from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.utils.config import settings


host = settings.database_host
port = settings.database_port
database = settings.database_name
username = settings.database_user
password = settings.database_password

engine = create_engine(
    f'postgresql://{username}:{password}@{host}:{port}/{database}'
)

Base = declarative_base()

from .user import User
from .store import Store
from .product import Product
from .product_details import ProductDetails
from .tag import Tag
from .product_tag import product_tag
from .recents import recents
from .favorites import favorites

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
