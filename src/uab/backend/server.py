"""Entry point for the backend."""


from fastapi import FastAPI
from uab.backend.app.data_access.database import engine, Base
from uab.backend.app.api.routes import router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Asset Browser",
    description="A cross-application asset browser for digital artists.",
    version="0.0.1",
)

app.include_router(router)
