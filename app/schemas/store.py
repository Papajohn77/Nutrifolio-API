from pydantic import BaseModel


class StoreBase(BaseModel):
    name: str
    logo_url: str
    location: str
    lat: float
    lng: float


class StoreOut(StoreBase):
    id: int

    class Config:
        orm_mode = True
