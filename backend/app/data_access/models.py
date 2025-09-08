"""SQLAlchemy models."""


from sqlalchemy import Column, Integer, String, Text
from .database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    description = Column(Text, nullable=True)
    file_path = Column(String)

    def __repr__(self):
        return f"<Asset(id={self.id}, name=`{self.name}`)>"
