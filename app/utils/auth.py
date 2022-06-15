from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.models import get_db
from app.models.user import User as user_model
from app.schemas.user import TokenData
from .config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail='Could not validate credentials',
                headers={"WWW-Authenticate":"Bearer"}
            )

        token_data = TokenData(id=user_id)
        return token_data
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail='Could not validate credentials',
            headers={"WWW-Authenticate":"Bearer"}
        )


def get_current_user(token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)):
    token = verify_access_token(token)
    db_user = db.query(user_model).filter(user_model.id == token.id).first()
    return db_user
