"""SQLAlchemy models."""


from sqlalchemy import Column, Integer, String, Text
from .database import Base


class Asset(Base):
    __tablename__ = "assets"

    # Base columns
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    directory_path = Column(String)

    type = Column(String, nullable=False)

    # VisualAsset Columns
    preview_image_file_path = Column(String, nullable=True)

    # Enable STI
    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "asset"
    }

    def __repr__(self):
        return f"<Asset(id={self.id}, name='{self.name}', type='{self.type}')>"

class VisualAsset(Asset):
    # Type for STI
    __mapper_args__ = {
        "polymorphic_identity": "visual_asset"
    }

    def get_preview_url(self):
        return self.preview_image_file_path if self.preview_image_file_path else None
