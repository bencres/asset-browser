"""API routes for browser CRUD operations."""
from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, or_, and_
from ..data_access import models, database
from ..api.schemas import AssetBase, AssetResponse


router = APIRouter(
    prefix="/assets",
    responses={404: {"description": "Not found"}},
)

# Get endpoints


@router.get("/", response_model=list[AssetResponse])
def get_all_assets(db: Session = Depends(database.get_db)):
    return db.query(models.Asset).all()


@router.get("/search", response_model=list[AssetResponse])
def search_assets(
    name: Optional[str] = Query(
        None, description="Search by asset name (partial match)"),
    tags: Optional[str] = Query(
        None, description="Search by tags (comma-separated)"),
    db: Session = Depends(database.get_db)
):
    """
    Search assets by name and/or tags.

    - name: Partial match search on asset name (case-insensitive)
    - tags: Comma-separated list of tags to search for
    """
    query = db.query(models.Asset)
    filters = []

    # Filter by name if provided
    if name:
        filters.append(models.Asset.name.ilike(f"%{name}%"))

    # Filter by tags if provided
    if tags:
        # Split comma-separated tags and search for any matching tag
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if tag_list:
            # For now, search in description field since tags column doesn't exist yet
            # TODO: Update this when tags column is added to the Asset model
            tag_filters = []
            for tag in tag_list:
                tag_filters.append(models.Asset.description.ilike(f"%{tag}%"))
            if tag_filters:
                filters.append(or_(*tag_filters))

    # Apply all filters
    if filters:
        query = query.filter(and_(*filters))

    return query.all()


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: int, db: Session = Depends(database.get_db)):
    db_asset = db.query(models.Asset).filter(
        models.Asset.id == asset_id).first()
    if db_asset is None:
        raise HTTPException(
            status_code=404, detail=f"Asset with id `{asset_id}` not found")
    return db_asset


# Post endpoints


@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(asset: AssetBase, db: Session = Depends(database.get_db)):
    db_asset = models.Asset(
        name=asset.name, description=asset.description, directory_path=asset.directory_path)
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


# Put endpoints

@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(asset_id: int, asset: AssetBase, db: Session = Depends(database.get_db)):
    db_asset = db.query(models.Asset).filter(
        models.Asset.id == asset_id).first()
    if db_asset is None:
        raise HTTPException(
            status_code=404, detail=f"Asset with id `{asset_id}` not found")

    db_asset.name = asset.name
    db_asset.description = asset.description
    db_asset.directory_path = asset.directory_path

    db.commit()
    db.refresh(db_asset)
    return db_asset


# Delete endpoints

@router.delete("/{asset_id}", response_model=AssetResponse)
def delete_asset(asset_id: int, db: Session = Depends(database.get_db)):
    db_asset = db.query(models.Asset).filter(
        models.Asset.id == asset_id).first()
    if db_asset is None:
        raise HTTPException(
            status_code=404, detail=f"Asset with id `{asset_id}` not found")

    db.delete(db_asset)
    db.commit()
    return db_asset


@router.delete("/admin/clear-database",
               status_code=status.HTTP_200_OK,
               response_model=Dict[str, str])
def clear_database(db: Session = Depends(database.get_db)):
    try:
        table_names = [
            table.name for table in models.Base.metadata.sorted_tables]
        for table_name in reversed(table_names):
            db.execute(text(f"DELETE FROM {table_name}"))

        db.commit()

        return {"message": "Database cleared successfully."}
    except Exception as e:
        db.rollback()  # Rollback if any errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear database: {e}"
        )
