from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query, BackgroundTasks

from src.models.support import SupportTicket, SupportMessage, TicketStatus
from src.schemas.support import (
    SupportTicketCreate,
    SupportMessageCreate,
    SupportTicketUpdate,
    SupportTicketResponse,
    SupportTicketDetailResponse,
    SupportTicketListResponse,
    SupportMessageResponse,
    SupportPaginatedResponse,
)
from src.api.deps import DbSession, CurrentUser, CurrentAdmin
from src.services.notification_service import notification_service

router = APIRouter(prefix="/support", tags=["support"])


@router.get("", response_model=SupportPaginatedResponse)
async def list_my_tickets(
    db: DbSession,
    user: CurrentUser,
    status_filter: Optional[TicketStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List current user's support tickets."""
    query = db.query(SupportTicket).filter(SupportTicket.user_id == user.id)
    
    if status_filter:
        query = query.filter(SupportTicket.status == status_filter)
    
    total = query.count()
    offset = (page - 1) * page_size
    
    tickets = (
        query
        .order_by(SupportTicket.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    
    pages = (total + page_size - 1) // page_size
    
    return SupportPaginatedResponse(
        items=[SupportTicketListResponse.model_validate(t) for t in tickets],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/admin", response_model=SupportPaginatedResponse)
async def list_all_tickets(
    db: DbSession,
    admin: CurrentAdmin,
    status_filter: Optional[TicketStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all support tickets (admin only)."""
    query = db.query(SupportTicket)
    
    if status_filter:
        query = query.filter(SupportTicket.status == status_filter)
    
    total = query.count()
    offset = (page - 1) * page_size
    
    tickets = (
        query
        .order_by(SupportTicket.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    
    pages = (total + page_size - 1) // page_size
    
    return SupportPaginatedResponse(
        items=[SupportTicketListResponse.model_validate(t) for t in tickets],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{ticket_id}", response_model=SupportTicketDetailResponse)
async def get_ticket(
    ticket_id: str,
    db: DbSession,
    user: CurrentUser,
):
    """Get a support ticket with messages."""
    ticket = db.query(SupportTicket).filter(SupportTicket.ticket_id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Only allow owner or admin to view
    if ticket.user_id != user.id and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get messages
    messages = (
        db.query(SupportMessage)
        .filter(SupportMessage.ticket_id == ticket.id)
        .order_by(SupportMessage.created_at.asc())
        .all()
    )
    
    response = SupportTicketDetailResponse.model_validate(ticket)
    response.messages = [SupportMessageResponse.model_validate(m) for m in messages]
    
    return response


@router.post("", response_model=SupportTicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: SupportTicketCreate,
    db: DbSession,
    user: CurrentUser,
    background_tasks: BackgroundTasks,
):
    """Create a new support ticket."""
    ticket = SupportTicket(
        user_id=user.id,
        subject=ticket_data.subject,
        message=ticket_data.message,
        priority=ticket_data.priority,
        status=TicketStatus.OPEN,
    )
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    # Send notifications in background
    background_tasks.add_task(
        notification_service.on_support_ticket_created,
        user=user,
        ticket_id=ticket.ticket_id,
        subject=ticket.subject,
        message=ticket.message,
    )
    
    return SupportTicketResponse.model_validate(ticket)


@router.post("/{ticket_id}/messages", response_model=SupportMessageResponse, status_code=status.HTTP_201_CREATED)
async def add_message(
    ticket_id: str,
    message_data: SupportMessageCreate,
    db: DbSession,
    user: CurrentUser,
    background_tasks: BackgroundTasks,
):
    """Add a message to a ticket (user reply)."""
    ticket = db.query(SupportTicket).filter(SupportTicket.ticket_id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    if ticket.user_id != user.id and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Don't allow messages on closed tickets
    if ticket.status == TicketStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add messages to closed tickets"
        )
    
    message = SupportMessage(
        ticket_id=ticket.id,
        user_id=user.id,
        is_staff_reply=user.is_admin,
        message=message_data.message,
    )
    
    db.add(message)
    
    # Update ticket status
    if user.is_admin:
        ticket.status = TicketStatus.WAITING_ON_CUSTOMER
        # Notify user of staff reply
        background_tasks.add_task(
            notification_service.on_support_reply,
            user=ticket.user,
            ticket_id=ticket.ticket_id,
            reply_content=message_data.message,
        )
    else:
        if ticket.status == TicketStatus.WAITING_ON_CUSTOMER:
            ticket.status = TicketStatus.IN_PROGRESS
    
    db.commit()
    db.refresh(message)
    
    return SupportMessageResponse.model_validate(message)


@router.put("/{ticket_id}", response_model=SupportTicketResponse)
async def update_ticket(
    ticket_id: str,
    ticket_data: SupportTicketUpdate,
    db: DbSession,
    admin: CurrentAdmin,
    background_tasks: BackgroundTasks,
):
    """Update ticket status (admin only)."""
    ticket = db.query(SupportTicket).filter(SupportTicket.ticket_id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    if ticket_data.status:
        ticket.status = ticket_data.status
        if ticket_data.status == TicketStatus.RESOLVED:
            ticket.resolved_at = datetime.utcnow()
    
    if ticket_data.priority:
        ticket.priority = ticket_data.priority
    
    if ticket_data.resolution_notes:
        ticket.resolution_notes = ticket_data.resolution_notes
    
    db.commit()
    db.refresh(ticket)
    
    return SupportTicketResponse.model_validate(ticket)


@router.post("/{ticket_id}/close", response_model=SupportTicketResponse)
async def close_ticket(
    ticket_id: str,
    db: DbSession,
    user: CurrentUser,
):
    """Close a ticket (user or admin)."""
    ticket = db.query(SupportTicket).filter(SupportTicket.ticket_id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    if ticket.user_id != user.id and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    ticket.status = TicketStatus.CLOSED
    if not ticket.resolved_at:
        ticket.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(ticket)
    
    return SupportTicketResponse.model_validate(ticket)
