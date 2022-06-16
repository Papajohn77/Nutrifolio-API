from sqlalchemy import Table, Column, ForeignKey
from . import Base

product_tag = Table(
    "product_tag",
    Base.metadata,
    Column("product_id", ForeignKey("products.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True)
)
