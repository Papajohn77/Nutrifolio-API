from typing import Optional
from pydantic import BaseModel, EmailStr, validator


class Token(BaseModel):
    access_token: str
    token_type: str


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    conf_password: str

    @validator('password')
    def password_strength(cls, password):
        if len(password) < 12:
            raise ValueError('Weak password: Should be at least 12 characters long')
        return password

    @validator('conf_password')
    def passwords_match(cls, conf_password, values, **kwargs):
        if 'password' in values and conf_password != values['password']:
            raise ValueError('Passwords do not match')
        return conf_password


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


class ProductDetailsOut(BaseModel):
    weight: int
    protein: int
    carbohydrates: int
    fiber: Optional[float] = None
    sugars: Optional[float] = None
    fat: int
    saturated_fat: Optional[float] = None

    class Config:
        orm_mode = True


class ProductDetailsCreate(ProductDetailsOut):
    product_id: int


class ProductBase(BaseModel):
    name: str
    description: str
    image_url: str
    calories: int
    price: float
    category: str


class ProductCreate(ProductBase):
    store_id: int


class ProductOutStore(ProductBase):
    id: int

    class Config:
        orm_mode = True


class StoreBase(BaseModel):
    name: str
    logo_url: str
    location: str
    lat: float
    lng: float


class StoreOut(StoreBase):
    id: int
    products: list[ProductOutStore] = []

    class Config:
        orm_mode = True


class StoreOutProduct(StoreBase):
    id: int

    class Config:
        orm_mode = True


class ProductOutSimple(ProductBase):
    id: int
    store: StoreOutProduct

    class Config:
        orm_mode = True


class ProductOutDetailed(ProductBase):
    id: int
    details: ProductDetailsOut
    store: StoreOutProduct

    class Config:
        orm_mode = True
