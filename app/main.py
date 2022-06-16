import logging
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from app.routers.user import users
from app.routers.store import stores
from app.routers.product import products
from app.models import SessionLocal
from app.models.recents import recents


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s')
handler = logging.FileHandler('/backend/logs/main.txt')
handler.setFormatter(formatter)

exception_logger = logging.getLogger(__name__)
exception_logger.addHandler(handler)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_methods = ["*"],
    allow_headers = ["*"],
    allow_credentials = True,
)

app.include_router(users)
app.include_router(stores)
app.include_router(products)


@app.on_event("startup")
@repeat_every(seconds=60*60)
def delete_expired_recents():
    try:
        not_recent_anymore = datetime.utcnow() - timedelta(days=3)

        with SessionLocal() as db:
            db.execute(
                recents.delete()
                    .where(recents.c.created_at < not_recent_anymore)
            )
            db.commit()
    except Exception as exc:
        exception_logger.exception(exc)
