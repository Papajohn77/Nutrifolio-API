from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import get_db
from app.models.product import Product
from app.models.product_details import ProductDetails
from app.models.recents import recents
from app.models.favorites import favorites
from app.schemas import ProductOutSimple, ProductOutDetailed, ProductCreate, ProductDetailsOut, ProductDetailsCreate, ProductOutStore, FavoritesOut, RecentsOut, FavoritesCreate, RecentsCreate
from app.utils import auth


products = APIRouter(
    tags=['Products']
)


def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


@products.get("/products/{id}", response_model=ProductOutDetailed)
def read_product(id: int, db: Session = Depends(get_db)):
    db_product = get_product_by_id(db, product_id=id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if db_product.details is None:
        raise HTTPException(
            status_code=500, detail="Product details missing")

    return db_product



@products.get("/favorites", response_model=FavoritesOut)
def read_favorites(current_user = Depends(auth.get_current_user)):
    return current_user


@products.get("/recents", response_model=RecentsOut)
def read_recents(current_user = Depends(auth.get_current_user)):
    return current_user


def insert_favorite(db: Session, user_id: int, product_id: int):
    db.execute(favorites.insert().values(
        user_id=user_id, product_id=product_id
    ))
    db.commit()


@products.post("/favorites", status_code=201)
def create_favorite(body: FavoritesCreate, db: Session = Depends(get_db),
        current_user = Depends(auth.get_current_user)):
    db_favorite = db.execute(
        favorites.select()
            .where(favorites.c.user_id == current_user.id)
            .where(favorites.c.product_id == body.product_id)
    ).first()

    if db_favorite:
        raise HTTPException(
            status_code=409, detail="Product already in favorites")

    insert_favorite(db, current_user.id, body.product_id)
    return {"ok": True}


def del_favorite(db: Session, user_id: int, product_id: int):
    db.execute(
        favorites.delete()
            .where(favorites.c.user_id == user_id)
            .where(favorites.c.product_id == product_id)
    )
    db.commit()


@products.delete("/favorites/{product_id}", status_code=204)
def delete_favorite(product_id: int, db: Session = Depends(get_db),
        current_user = Depends(auth.get_current_user)):
    db_favorite = db.execute(
        favorites.select()
            .where(favorites.c.user_id == current_user.id)
            .where(favorites.c.product_id == product_id)
    ).first()

    if not db_favorite:
        raise HTTPException(
            status_code=409, detail="Product not in favorites")

    del_favorite(db, current_user.id, product_id)
    return Response(status_code=204)


def insert_recent(db: Session, user_id: int, product_id: int):
    db.execute(recents.insert().values(
        user_id=user_id, product_id=product_id
    ))
    db.commit()


def upd_recent(db: Session, user_id: int, product_id: int):
    db.execute(
        recents.update()
            .where(recents.c.user_id == user_id)
            .where(recents.c.product_id == product_id)
            .values(created_at=datetime.utcnow())
    )
    db.commit()


@products.post("/recents", status_code=201)
def create_recent(body: RecentsCreate, db: Session = Depends(get_db),
        current_user = Depends(auth.get_current_user)):
    db_recent = db.execute(
        recents.select()
            .where(recents.c.user_id == current_user.id)
            .where(recents.c.product_id == body.product_id)
    ).first()

    if not db_recent:
        insert_recent(db, current_user.id, body.product_id)
    else:
        upd_recent(db, current_user.id, body.product_id)

    return {"ok": True}


def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Product).offset(skip).limit(limit).all()


@products.get('/products', response_model=list[ProductOutSimple])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = get_products(db, skip=skip, limit=limit)
    return products


def insert_product(db: Session, product: ProductCreate):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@products.post('/products', response_model=ProductOutStore)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = insert_product(db=db, product=product)
    return new_product


def insert_product_details(db: Session, product_details: ProductDetailsCreate):
    db_product_details = ProductDetails(**product_details.dict())
    db.add(db_product_details)
    db.commit()
    db.refresh(db_product_details)
    return db_product_details


@products.post('/product-details', response_model=ProductDetailsOut)
def create_product_details(product_details: ProductDetailsCreate,
        db: Session = Depends(get_db)):
    new_product_details = insert_product_details(
        db=db, product_details=product_details)
    return new_product_details
