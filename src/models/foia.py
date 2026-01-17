import enum
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, Enum, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.document import SourceDocument
    from src.models.article import Article


class FOIAStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    PROCESSING = "processing"
    PARTIAL_RESPONSE = "partial_response"
    COMPLETED = "completed"
    DENIED = "denied"
    APPEALED = "appealed"
    WITHDRAWN = "withdrawn"


class FOIARequest(Base, TimestampMixin):
    __tablename__ = "foia_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Request details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    agency: Mapped[str] = mapped_column(String(255), nullable=False)
    agency_contact: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    request_text: Mapped[str] = mapped_column(Text, nullable=False)  # Full request content
    
    # Status tracking
    status: Mapped[FOIAStatus] = mapped_column(Enum(FOIAStatus), default=FOIAStatus.DRAFT)
    tracking_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Dates
    request_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expected_response_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_response_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    follow_up_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Response notes
    response_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    denial_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Link to article (if used in a story)
    related_article_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("articles.id"), nullable=True
    )
    related_article: Mapped[Optional["Article"]] = relationship("Article")
    
    # Documents received
    documents: Mapped[List["SourceDocument"]] = relationship(
        "SourceDocument", back_populates="foia_request", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<FOIARequest {self.title}>"
