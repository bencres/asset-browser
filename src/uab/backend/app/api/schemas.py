"""Pydantic models for API request/response."""

from pydantic import BaseModel
from typing import Optional


class AssetBase(BaseModel):
    name: str
    description: Optional[str] = None
    directory_path: str
    preview_image_file_path: Optional[str] = None


class AssetResponse(AssetBase):
    id: int


    class Config:
        orm_mode = True # For SQLAlchemy models
