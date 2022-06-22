import itertools
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from app.models import get_db
from app.models.store import Store
from app.schemas import StoreBase, StoreOut, StoreOutProduct


stores = APIRouter(
    tags=['Stores']
)


class StoreDoesNotExist(Exception):
    pass


def get_store_by_id(db: Session, store_id: int):
    return db.query(Store).filter(Store.id == store_id).first()


@stores.get("/stores/{id}", response_model=StoreOut)
def read_store(id: int, db: Session = Depends(get_db)):
    try:
        db_store = get_store_by_id(db, store_id=id)
        if not db_store:
            raise StoreDoesNotExist("Store not found.")

        products = []
        for key, group in itertools.groupby(db_store.products,
                lambda product: product.category):

            category_products = []
            for product in group:
                category_products.append({
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "image_url": product.image_url,
                    "calories": product.calories,
                    "price": product.price
                })

            products.append({
                "category": key,
                "products": category_products
            })

        return {
            "id": db_store.id,
            "name": db_store.name,
            "logo_url": db_store.logo_url,
            "location": db_store.location,
            "lat": db_store.lat,
            "lng": db_store.lng,
            "products": products
        }
    except StoreDoesNotExist as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load store.")


@stores.get("/search")
def search_stores(q: str, lat: float, lng: float, distance: float = 3,
        skip: int = 0,  limit: int = 100, db: Session = Depends(get_db)):
    try:
        stmt = text("""
            SELECT * 
            FROM (SELECT *, 
                    (
                        (
                            (
                                acos(
                                    sin((:lat * pi() / 180))
                                    *
                                    sin((s.lat * pi() / 180))
                                    +
                                    cos((:lat * pi() / 180))
                                    *
                                    cos((s.lat * pi() / 180))
                                    *
                                    cos(((:lng - s.lng) * pi() / 180))
                                )
                            ) * 180 / pi()
                        ) * 60 * 1.1515 * 1.609344
                    ) AS distance FROM stores AS s
            ) AS stores_with_dist
            WHERE distance <= :distance AND name ILIKE :q
            LIMIT :limit OFFSET :skip
        """)

        params = {
            "q": f'%{q}%',
            "lat": lat,
            "lng": lng,
            "distance": distance,
            "limit": limit,
            "skip": skip
        }
        near_stores = db.execute(stmt, params).fetchall()
        return {"stores": near_stores}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to search stores.")


def get_stores(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Store).offset(skip).limit(limit).all()


@stores.get('/stores', response_model=list[StoreOutProduct])
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


@stores.post('/stores', response_model=StoreOutProduct)
def create_store(store: StoreBase, db: Session = Depends(get_db)):
    db_store = get_store_by_name(db, store.name)
    if db_store:
        raise HTTPException(status_code=409, detail="Store name already used.")

    new_store = insert_store(db=db, store=store)
    return new_store
