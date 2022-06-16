from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from . import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    logo_url = Column(String, nullable=False)
    location = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)

    products = relationship(
        "Product",
        back_populates="store",
        order_by="desc(Product.category)",
        cascade="all, delete"
    )
