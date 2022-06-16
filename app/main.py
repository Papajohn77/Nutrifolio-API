from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.user import users
from app.routers.store import stores
from app.routers.product import products


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
