import enum
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Enum, ForeignKey, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin
from src.models.user import SubscriptionTier

if TYPE_CHECKING:
    from src.models.article import Article
    from src.models.foia import FOIARequest


class DocumentType(str, enum.Enum):
    PDF = "pdf"
    IMAGE = "image"
    SPREADSHEET = "spreadsheet"
    TEXT = "text"
    VIDEO = "video"
    OTHER = "other"


class SourceDocument(Base, TimestampMixin):
    __tablename__ = "source_documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Document details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType), default=DocumentType.PDF
    )
    
    # Storage
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Local path
    s3_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # S3 key
    external_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # External link
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Bytes
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Access control
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    tier_required: Mapped[SubscriptionTier] = mapped_column(
        Enum(SubscriptionTier), default=SubscriptionTier.FREE
    )
    
    # Source attribution
    source_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    document_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    
    # Relationships
    article_id: Mapped[Optional[int]] = mapped_column(ForeignKey("articles.id"), nullable=True)
    article: Mapped[Optional["Article"]] = relationship("Article", back_populates="source_documents")
    
    foia_request_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("foia_requests.id"), nullable=True
    )
    foia_request: Mapped[Optional["FOIARequest"]] = relationship(
        "FOIARequest", back_populates="documents"
    )

    def __repr__(self) -> str:
        return f"<SourceDocument {self.title}>"
