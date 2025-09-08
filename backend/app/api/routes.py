"""API routes for browser CRUD operations."""


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..data_access import models, database
from ..api.schemas import AssetBase, AssetResponse


router = APIRouter(
    prefix="/assets",
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[AssetResponse])
def get_all_assets(db: Session = Depends(database.get_db)):
    return db.query(models.Asset).all()


@router.post("/", response_model=AssetResponse)
def create_asset(asset: AssetBase, db: Session = Depends(database.get_db)):
    db_asset = models.Asset(name=asset.name, description=asset.description, file_path=asset.file_path)
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(asset_id: int, asset: AssetBase, db: Session = Depends(database.get_db)):
    db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if db_asset is None:
        raise HTTPException(status_code=404, detail=f"Asset with id `{asset_id}` not found")

    db_asset.name = asset.name
    db_asset.description = asset.description
    db_asset.file_path = asset.file_path

    db.commit()
    db.refresh(db_asset)
    return db_asset


@router.delete("/{asset_id}", response_model=AssetResponse)
def delete_asset(asset_id: int, db: Session = Depends(database.get_db)):
    db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if db_asset is None:
        raise HTTPException(status_code=404, detail=f"Asset with id `{asset_id}` not found")

    db.delete(db_asset)
    db.commit()
    return db_asset
