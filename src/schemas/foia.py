from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field

from src.models.foia import FOIAStatus


class FOIARequestBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    agency: str = Field(..., min_length=1, max_length=255)
    agency_contact: Optional[str] = Field(None, max_length=500)
    topic: str = Field(..., min_length=1)
    request_text: str = Field(..., min_length=1)


class FOIARequestCreate(FOIARequestBase):
    """Schema for creating a new FOIA request."""
    request_date: Optional[date] = None  # Auto-set if not provided


class FOIARequestUpdate(BaseModel):
    """Schema for updating a FOIA request."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    agency: Optional[str] = Field(None, min_length=1, max_length=255)
    agency_contact: Optional[str] = Field(None, max_length=500)
    topic: Optional[str] = None
    request_text: Optional[str] = None
    status: Optional[FOIAStatus] = None
    tracking_number: Optional[str] = Field(None, max_length=255)
    request_date: Optional[date] = None
    expected_response_date: Optional[date] = None
    actual_response_date: Optional[date] = None
    follow_up_date: Optional[date] = None
    response_notes: Optional[str] = None
    denial_reason: Optional[str] = None
    related_article_id: Optional[int] = None


class FOIAStatusUpdate(BaseModel):
    """Schema for updating FOIA request status."""
    status: FOIAStatus
    tracking_number: Optional[str] = None
    response_notes: Optional[str] = None
    denial_reason: Optional[str] = None
    actual_response_date: Optional[date] = None


class FOIARequestResponse(BaseModel):
    """Schema for FOIA request response."""
    id: int
    title: str
    agency: str
    agency_contact: Optional[str]
    topic: str
    request_text: str
    status: FOIAStatus
    tracking_number: Optional[str]
    request_date: Optional[date]
    expected_response_date: Optional[date]
    actual_response_date: Optional[date]
    follow_up_date: Optional[date]
    response_notes: Optional[str]
    denial_reason: Optional[str]
    related_article_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FOIARequestListResponse(BaseModel):
    """Schema for FOIA request list item."""
    id: int
    title: str
    agency: str
    status: FOIAStatus
    tracking_number: Optional[str]
    request_date: Optional[date]
    expected_response_date: Optional[date]
    follow_up_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


class FOIAPaginatedResponse(BaseModel):
    """Paginated list of FOIA requests."""
    items: List[FOIARequestListResponse]
    total: int
    page: int
    page_size: int
    pages: int


class FOIAReminderResponse(BaseModel):
    """FOIA requests due for follow-up."""
    overdue: List[FOIARequestListResponse]
    due_soon: List[FOIARequestListResponse]  # Due within 7 days
