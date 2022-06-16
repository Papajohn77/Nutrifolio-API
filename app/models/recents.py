from sqlalchemy import Table, Column, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from . import Base


recents = Table(
    "recents",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
)
