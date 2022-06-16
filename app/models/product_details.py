from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from . import Base


class ProductDetails(Base):
    __tablename__ = "product_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    weight = Column(Integer, nullable=False)
    protein = Column(Integer, nullable=False)
    carbohydrates = Column(Integer, nullable=False)
    fiber = Column(Float)
    sugars = Column(Float)
    fat = Column(Integer, nullable=False)
    saturated_fat = Column(Float)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"),
        unique=True, nullable=False)
