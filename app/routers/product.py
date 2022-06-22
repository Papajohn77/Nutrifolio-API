from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import get_db
from app.models.product import Product
from app.models.product_details import ProductDetails
from app.models.recents import recents
from app.models.favorites import favorites
from app.schemas import ProductOutSimple, ProductOutDetailed, ProductCreate, ProductDetailsOut, ProductDetailsCreate, ProductOutStore, FavoritesOut, RecentsOut, FavoritesCreate, RecentsCreate, Filters
from app.utils import auth


products = APIRouter(
    tags=['Products']
)


class ProductDoesNotExist(Exception):
    pass


class ProductDetailsMissing(Exception):
    pass


def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


@products.get("/products/{id}", response_model=ProductOutDetailed)
def read_product(id: int, db: Session = Depends(get_db)):
    try:
        db_product = get_product_by_id(db, product_id=id)
        if not db_product:
            raise ProductDoesNotExist("Product not found.")

        if not db_product.details:
            raise ProductDetailsMissing("Product details missing.")

        return db_product
    except ProductDoesNotExist as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ProductDetailsMissing as error:
        raise HTTPException(status_code=500, detail=str(error))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load product.")


@products.get("/favorites", response_model=FavoritesOut)
def read_favorites(current_user = Depends(auth.get_current_user)):
    return current_user


@products.get("/recents", response_model=RecentsOut)
def read_recents(current_user = Depends(auth.get_current_user)):
    return current_user


class ProductAlreadyInFavorites(Exception):
    pass


def get_favorite(db: Session, user_id: int, product_id: int):
    db_favorite = db.execute(
        favorites.select()
            .where(favorites.c.user_id == user_id)
            .where(favorites.c.product_id == product_id)
    ).first()

    return db_favorite


def insert_favorite(db: Session, user_id: int, product_id: int):
    db.execute(
        favorites.insert().values(user_id=user_id, product_id=product_id)
    )
    db.commit()


@products.post("/favorites", response_model=ProductOutSimple, status_code=201)
def create_favorite(body: FavoritesCreate, db: Session = Depends(get_db),
        current_user = Depends(auth.get_current_user)):
    try:
        db_favorite = get_favorite(db, current_user.id, body.product_id)
        if db_favorite:
            raise ProductAlreadyInFavorites("Product already in favorites.")

        insert_favorite(db, current_user.id, body.product_id)
        return get_product_by_id(db, body.product_id)
    except ProductAlreadyInFavorites as error:
        raise HTTPException(status_code=409, detail=str(error))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to create favorite.")


class ProductNotInFavorites(Exception):
    pass


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
    try:
        db_favorite = get_favorite(db, current_user.id, product_id)
        if not db_favorite:
            raise ProductNotInFavorites("Product not in favorites.")

        del_favorite(db, current_user.id, product_id)
        return Response(status_code=204)
    except ProductNotInFavorites as error:
        raise HTTPException(status_code=409, detail=str(error))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to delete favorite.")


def get_recent(db: Session, user_id: int, product_id: int):
    db_recent = db.execute(
        recents.select()
            .where(recents.c.user_id == user_id)
            .where(recents.c.product_id == product_id)
    ).first()

    return db_recent


def insert_recent(db: Session, user_id: int, product_id: int):
    db.execute(
        recents.insert().values(user_id=user_id, product_id=product_id)
    )
    db.commit()


def upd_recent(db: Session, user_id: int, product_id: int):
    db.execute(
        recents.update()
            .where(recents.c.user_id == user_id)
            .where(recents.c.product_id == product_id)
            .values(created_at=datetime.utcnow())
    )
    db.commit()


@products.post("/recents", response_model=ProductOutSimple, status_code=201)
def create_recent(body: RecentsCreate, db: Session = Depends(get_db),
        current_user = Depends(auth.get_current_user)):
    try:
        db_recent = get_recent(db, current_user.id, body.product_id)

        if not db_recent:
            insert_recent(db, current_user.id, body.product_id)
        else:
            upd_recent(db, current_user.id, body.product_id)

        return get_product_by_id(db, body.product_id)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to create recent.")


@products.post("/filter")
def filter_products(filters: Filters, skip: int = 0, 
        limit: int = 100, db: Session = Depends(get_db)):
    try:
        stmt = (
            select(text("""
                p.id, p.name, description, price, calories, image_url, 
                distance, s.id, s.name, logo_url
            """))
            .select_from(text("""
                (SELECT *,
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
                ) AS s
            """))
            .select_from(text('products AS p'))
            .select_from(text('product_details AS pd'))
            .where(text('s.id = p.store_id'))
            .where(text('p.id = pd.product_id'))
        )

        if filters.max_dist is not None:
            stmt = stmt.where(text('distance <= :max_dist'))

        if filters.min_price is not None and filters.max_price is not None:
            stmt = stmt.where(text('(price BETWEEN :min_price AND :max_price)'))

        if filters.min_calories is not None and filters.max_calories is not None:
            stmt = stmt.where(text('(calories BETWEEN :min_calories AND :max_calories)'))

        if filters.min_protein is not None and filters.max_protein is not None:
            stmt = stmt.where(text('(protein BETWEEN :min_protein AND :max_protein)'))

        if filters.min_carbs is not None and filters.max_carbs is not None:
            stmt = stmt.where(text('(carbohydrates BETWEEN :min_carbs AND :max_carbs)'))

        if filters.min_fat is not None and filters.max_fat is not None:
            stmt = stmt.where(text('(fat BETWEEN :min_fat AND :max_fat)'))

        if filters.categories is not None:
            stmt = (stmt.select_from(text('product_tag AS pt'))
                        .select_from(text('tags AS t'))
                        .where(text('p.id = pt.product_id'))
                        .where(text('pt.tag_id = t.id'))
                        .where(text('label IN :categories'))
            )

        if filters.sort_by is not None and filters.ordering is not None:
            stmt = stmt.order_by(text(f'{filters.sort_by} {filters.ordering}'))

        stmt = stmt.limit(limit).offset(skip)

        db_products = db.execute(stmt, dict(filters)).fetchall()
        distinct_db_products = list(dict.fromkeys(db_products)) # Preserves order

        response = []
        for p_id, p_name, description, price, calories, image_url, \
                distance, s_id, s_name, logo_url in distinct_db_products:
            response.append({
                "id": p_id,
                "name": p_name,
                "description": description,
                "price": price,
                "calories": calories,
                "image_url": image_url,
                "distance": distance,
                "store": {
                    "id": s_id,
                    "name": s_name,
                    "logo_url": logo_url
                }
            })
        return {"products": response}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to filter products.")


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
