from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import get_db
from app.models.store import Store
from app.schemas import StoreBase, StoreOut


stores = APIRouter(
    tags=['Stores']
)


def get_store_by_id(db: Session, store_id: int):
    return db.query(Store).filter(Store.id == store_id).first()


@stores.get("/stores/{id}", response_model=StoreOut)
def read_store(id: int, db: Session = Depends(get_db)):
    db_store = get_store_by_id(db, store_id=id)
    if not db_store:
        raise HTTPException(status_code=404, detail="Store not found")
    return db_store


def get_stores(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Store).offset(skip).limit(limit).all()


@stores.get('/stores', response_model=list[StoreOut])
def read_stores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stores = get_stores(db, skip=skip, limit=limit)
    return stores


def get_store_by_name(db: Session, name: str):
    return db.query(Store).filter(Store.name == name).first()


def insert_store(db: Session, store: StoreBase):
    db_store = Store(**store.dict())
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store


@stores.post('/stores', response_model=StoreOut)
def create_store(store: StoreBase, db: Session = Depends(get_db)):
    db_store = get_store_by_name(db, store.name)
    if db_store:
        raise HTTPException(status_code=400, detail="Store name already taken")

    new_store = insert_store(db=db, store=store)
    return new_store
