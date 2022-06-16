from sqlalchemy import Table, Column, ForeignKey
from . import Base


favorites = Table(
    "favorites",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True)
)
