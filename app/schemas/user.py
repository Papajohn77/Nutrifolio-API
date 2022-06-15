from typing import Optional
from pydantic import BaseModel, EmailStr, validator


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
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


class UserOut(BaseModel):
    id: int
    first_name: str
    email: EmailStr

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
