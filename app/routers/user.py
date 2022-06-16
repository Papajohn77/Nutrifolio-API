from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models import get_db
from app.models.user import User
from app.schemas import UserOut, UserCreate, Token
from app.utils import auth


users = APIRouter(
    tags=['Users']
)

myctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


@users.post('/login', response_model=Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm's username corresponds to the email
    db_user = get_user_by_email(db, user_credentials.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not myctx.verify(user_credentials.password, db_user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = auth.create_access_token(data = {"user_id": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}


def insert_user(db: Session, user: UserCreate):
    hashed_password = myctx.hash(user.password)
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@users.post('/signup', response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = insert_user(db=db, user=user)
    access_token = auth.create_access_token(data = {"user_id": new_user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@users.get("/users/{id}", response_model=UserOut)
def read_user(id: int, current_user = Depends(auth.get_current_user)):
    if current_user.id != id:
        raise HTTPException(
            status_code=403, detail="Can not access other users' data")
    return current_user
