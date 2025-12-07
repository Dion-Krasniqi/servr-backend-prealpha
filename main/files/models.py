from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy import ForeignKey, String, DateTime

from datetime import datetime
import uuid

class Base(DeclarativeBase):
    pass

class FilePSQL(Base):
    __tablename__ = "files"
    file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    filename: Mapped[str]
    extension: Mapped[str]
    bucket: Mapped[str]
    size: Mapped[int]
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    shared_with: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    url: Mapped[str]
    createdat: Mapped[datetime] = mapped_column(DateTime(timezone=False))
    lastmodified: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    file_type: Mapped[str]


