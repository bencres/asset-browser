"""API routes for browser CRUD operations."""


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..data_access import models, database
from ..api.schemas import AssetBase, AssetResponse


router = APIRouter(
    prefix="/assets",
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=AssetResponse)
def create_asset(asset: AssetBase, db: Session = Depends(database.get_db())):
    db_asset = models.Asset(name=asset.name, description=asset.description, file_path=asset.file_path)
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset
