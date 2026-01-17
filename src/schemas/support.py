from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from src.models.support import TicketStatus, TicketPriority


class SupportTicketCreate(BaseModel):
    """Schema for creating a support ticket."""
    subject: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=10)
    priority: TicketPriority = TicketPriority.NORMAL


class SupportMessageCreate(BaseModel):
    """Schema for adding a message to a ticket."""
    message: str = Field(..., min_length=1)


class SupportTicketUpdate(BaseModel):
    """Schema for updating a ticket (admin)."""
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    resolution_notes: Optional[str] = None


class SupportMessageResponse(BaseModel):
    """Schema for support message response."""
    id: int
    is_staff_reply: bool
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class SupportTicketResponse(BaseModel):
    """Schema for support ticket response."""
    id: int
    ticket_id: str
    subject: str
    message: str
    status: TicketStatus
    priority: TicketPriority
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SupportTicketDetailResponse(SupportTicketResponse):
    """Detailed ticket response with messages."""
    messages: List[SupportMessageResponse] = []


class SupportTicketListResponse(BaseModel):
    """Schema for ticket list item."""
    id: int
    ticket_id: str
    subject: str
    status: TicketStatus
    priority: TicketPriority
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SupportPaginatedResponse(BaseModel):
    """Paginated list of support tickets."""
    items: List[SupportTicketListResponse]
    total: int
    page: int
    page_size: int
    pages: int
