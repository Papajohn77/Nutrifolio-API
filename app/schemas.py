from typing import Optional
from pydantic import BaseModel, validator
from email_validator import validate_email, EmailNotValidError


class Token(BaseModel):
    access_token: str
    token_type: str


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str


class UserCreate(UserBase):
    password: str
    conf_password: str

    @validator('first_name')
    def first_name_validation(cls, first_name):
        if not first_name:
            raise ValueError('First Name is required.')

    @validator('last_name')
    def last_name_validation(cls, last_name):
        if not last_name:
            raise ValueError('Last Name is required.')

    @validator('email')
    def email_validation(cls, email):
        validate_email(email)
        return email

    @validator('password')
    def password_strength(cls, password):
        if len(password) < 12:
            raise ValueError(
                'Weak password: Should be at least 12 characters long.')
        return password

    @validator('conf_password')
    def passwords_match(cls, conf_password, values, **kwargs):
        if 'password' in values and conf_password != values['password']:
            raise ValueError('Passwords do not match.')
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


class ProductCreate(ProductBase):
    category: str
    store_id: int


class ProductOutStore(ProductBase):
    id: int

    class Config:
        orm_mode = True


class CategoryProducts(BaseModel):
    category: str
    products: list[ProductOutStore] = []

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
    products: list[CategoryProducts] = []

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


class FavoritesOut(BaseModel):
    favorites: list[ProductOutSimple]

    class Config:
        orm_mode = True


class FavoritesCreate(BaseModel):
    product_id: int


class RecentsOut(BaseModel):
    recents: list[ProductOutSimple]

    class Config:
        orm_mode = True


class RecentsCreate(BaseModel):
    product_id: int


class Filters(BaseModel):
    lat: float
    lng: float
    categories: Optional[tuple[str, ...]] = None
    max_dist: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_calories: Optional[int] = None
    max_calories: Optional[int] = None
    min_protein: Optional[int] = None
    max_protein: Optional[int] = None
    min_carbs: Optional[int] = None
    max_carbs: Optional[int] = None
    min_fat: Optional[int] = None
    max_fat: Optional[int] = None
    sort_by: Optional[str] = None
    ordering: Optional[str] = None

    @validator('categories')
    def categories_validation(cls, categories):
        valid_categories = [
            'Vegan', 'Vegeterian', 'Sugar Free',
            'Gluten Free', 'Lactose Free', 'Pescatarian'
        ]

        for categ in categories:
            if categ not in valid_categories:
                raise ValueError('Invalid categories')
        return categories

    @validator('sort_by')
    def sort_by_validation(cls, sort_by):
        valid_sort_by = ['price', 'distance', 'calories', 'protein']

        if sort_by not in valid_sort_by:
            raise ValueError('Invalid sort_by')
        return sort_by

    @validator('ordering')
    def ordering_validation(cls, ordering):
        valid_orderings = ['ASC', 'DESC']

        if ordering not in valid_orderings:
            raise ValueError('Invalid ordering')
        return ordering
