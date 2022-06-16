from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import get_db
from app.models.product import Product
from app.models.product_details import ProductDetails
from app.schemas import ProductOutSimple, ProductOutDetailed, ProductCreate, ProductDetailsOut, ProductDetailsCreate, ProductOutStore


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
            status_code=500, detail="Nutritional values missing...")

    return db_product


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
