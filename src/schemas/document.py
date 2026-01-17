from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from src.models.document import DocumentType
from src.models.user import SubscriptionTier


class DocumentCreate(BaseModel):
    """Schema for creating a document record (after upload)."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    document_type: DocumentType = DocumentType.PDF
    is_public: bool = False
    tier_required: SubscriptionTier = SubscriptionTier.FREE
    source_name: Optional[str] = Field(None, max_length=255)
    source_url: Optional[str] = Field(None, max_length=500)
    document_date: Optional[datetime] = None
    article_id: Optional[int] = None
    foia_request_id: Optional[int] = None


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    is_public: Optional[bool] = None
    tier_required: Optional[SubscriptionTier] = None
    source_name: Optional[str] = Field(None, max_length=255)
    source_url: Optional[str] = Field(None, max_length=500)
    document_date: Optional[datetime] = None
    article_id: Optional[int] = None
    foia_request_id: Optional[int] = None


class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: int
    title: str
    description: Optional[str]
    document_type: DocumentType
    file_size: Optional[int]
    mime_type: Optional[str]
    is_public: bool
    tier_required: SubscriptionTier
    source_name: Optional[str]
    source_url: Optional[str]
    document_date: Optional[datetime]
    article_id: Optional[int]
    foia_request_id: Optional[int]
    download_url: Optional[str] = None  # Added dynamically
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for document list item."""
    id: int
    title: str
    document_type: DocumentType
    file_size: Optional[int]
    is_public: bool
    tier_required: SubscriptionTier
    source_name: Optional[str]
    article_id: Optional[int]
    foia_request_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentPaginatedResponse(BaseModel):
    """Paginated list of documents."""
    items: List[DocumentListResponse]
    total: int
    page: int
    page_size: int
    pages: int


class UploadResponse(BaseModel):
    """Response after file upload."""
    document_id: int
    title: str
    download_url: Optional[str]
