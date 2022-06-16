from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from . import Base
from .product_tag import product_tag


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String, unique=True, nullable=False)

    products = relationship(
        "Product", secondary=product_tag, back_populates="tags"
    )
