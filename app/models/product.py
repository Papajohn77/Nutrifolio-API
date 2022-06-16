from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from . import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    calories = Column(Integer, nullable=False)
    price = Column(Numeric, nullable=False)
    category = Column(String, nullable=False)  # Menu Category
    store_id = Column(Integer, ForeignKey(
        "stores.id", ondelete="CASCADE"), nullable=False)

    details = relationship("ProductDetails", uselist=False)
    store = relationship("Store", back_populates="products")
