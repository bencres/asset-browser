"""Entry point for the backend."""


from fastapi import FastAPI
from app.data_access.database import engine, Base
from app.api.routes import router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Asset Browser",
    description="A cross-application asset browser for digital artists.",
    version="0.0.1",
)

app.include_router(router)
