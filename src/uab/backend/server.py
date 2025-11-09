"""Entry point for the backend."""


from fastapi import FastAPI
from uab.backend.app.data_access.database import engine, Base
from uab.backend.app.api.routes import router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Universal Asset Browser",
    description="A cross-application asset browser for digital artists.",
    version="0.0.1",
)

print(f"Connecting to DB at {engine.url}")

app.include_router(router)
