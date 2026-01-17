from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query

from src.models import FOIARequest, FOIAStatus
from src.schemas.foia import (
    FOIARequestCreate,
    FOIARequestUpdate,
    FOIAStatusUpdate,
    FOIARequestResponse,
    FOIARequestListResponse,
    FOIAPaginatedResponse,
    FOIAReminderResponse,
)
from src.api.deps import DbSession, CurrentAdmin

router = APIRouter(prefix="/foia", tags=["foia"])


def calculate_expected_response_date(request_date: date) -> date:
    """Calculate expected response date (20 business days from request)."""
    current = request_date
    business_days = 0
    
    while business_days < 20:
        current += timedelta(days=1)
        # Skip weekends
        if current.weekday() < 5:  # Monday = 0, Friday = 4
            business_days += 1
    
    return current


@router.get("", response_model=FOIAPaginatedResponse)
async def list_foia_requests(
    db: DbSession,
    admin: CurrentAdmin,
    status_filter: Optional[FOIAStatus] = Query(None, alias="status"),
    agency: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all FOIA requests (admin only)."""
    query = db.query(FOIARequest)
    
    if status_filter:
        query = query.filter(FOIARequest.status == status_filter)
    if agency:
        query = query.filter(FOIARequest.agency.ilike(f"%{agency}%"))
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            FOIARequest.title.ilike(search_term) |
            FOIARequest.topic.ilike(search_term) |
            FOIARequest.agency.ilike(search_term)
        )
    
    total = query.count()
    offset = (page - 1) * page_size
    
    requests = (
        query
        .order_by(FOIARequest.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    
    pages = (total + page_size - 1) // page_size
    
    return FOIAPaginatedResponse(
        items=[FOIARequestListResponse.model_validate(r) for r in requests],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/reminders", response_model=FOIAReminderResponse)
async def get_foia_reminders(
    db: DbSession,
    admin: CurrentAdmin,
):
    """Get FOIA requests that need attention (overdue or due soon)."""
    today = date.today()
    week_from_now = today + timedelta(days=7)
    
    # Active statuses that we're waiting on
    active_statuses = [
        FOIAStatus.SUBMITTED,
        FOIAStatus.ACKNOWLEDGED,
        FOIAStatus.PROCESSING,
    ]
    
    # Overdue requests
    overdue = (
        db.query(FOIARequest)
        .filter(
            FOIARequest.status.in_(active_statuses),
            FOIARequest.expected_response_date < today,
        )
        .order_by(FOIARequest.expected_response_date.asc())
        .all()
    )
    
    # Due within 7 days
    due_soon = (
        db.query(FOIARequest)
        .filter(
            FOIARequest.status.in_(active_statuses),
            FOIARequest.expected_response_date >= today,
            FOIARequest.expected_response_date <= week_from_now,
        )
        .order_by(FOIARequest.expected_response_date.asc())
        .all()
    )
    
    return FOIAReminderResponse(
        overdue=[FOIARequestListResponse.model_validate(r) for r in overdue],
        due_soon=[FOIARequestListResponse.model_validate(r) for r in due_soon],
    )


@router.get("/{foia_id}", response_model=FOIARequestResponse)
async def get_foia_request(
    foia_id: int,
    db: DbSession,
    admin: CurrentAdmin,
):
    """Get a single FOIA request by ID."""
    foia = db.query(FOIARequest).filter(FOIARequest.id == foia_id).first()
    
    if not foia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FOIA request not found"
        )
    
    return FOIARequestResponse.model_validate(foia)


@router.post("", response_model=FOIARequestResponse, status_code=status.HTTP_201_CREATED)
async def create_foia_request(
    foia_data: FOIARequestCreate,
    db: DbSession,
    admin: CurrentAdmin,
):
    """Create a new FOIA request record."""
    request_date = foia_data.request_date or date.today()
    expected_response = calculate_expected_response_date(request_date)
    
    foia = FOIARequest(
        title=foia_data.title,
        agency=foia_data.agency,
        agency_contact=foia_data.agency_contact,
        topic=foia_data.topic,
        request_text=foia_data.request_text,
        status=FOIAStatus.DRAFT,
        request_date=request_date,
        expected_response_date=expected_response,
        follow_up_date=expected_response,  # Initial follow-up = expected response
    )
    
    db.add(foia)
    db.commit()
    db.refresh(foia)
    
    return FOIARequestResponse.model_validate(foia)


@router.put("/{foia_id}", response_model=FOIARequestResponse)
async def update_foia_request(
    foia_id: int,
    foia_data: FOIARequestUpdate,
    db: DbSession,
    admin: CurrentAdmin,
):
    """Update a FOIA request."""
    foia = db.query(FOIARequest).filter(FOIARequest.id == foia_id).first()
    
    if not foia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FOIA request not found"
        )
    
    update_data = foia_data.model_dump(exclude_unset=True)
    
    # Recalculate expected response date if request date changed
    if "request_date" in update_data and update_data["request_date"]:
        update_data["expected_response_date"] = calculate_expected_response_date(
            update_data["request_date"]
        )
    
    for field, value in update_data.items():
        setattr(foia, field, value)
    
    db.commit()
    db.refresh(foia)
    
    return FOIARequestResponse.model_validate(foia)


@router.post("/{foia_id}/status", response_model=FOIARequestResponse)
async def update_foia_status(
    foia_id: int,
    status_data: FOIAStatusUpdate,
    db: DbSession,
    admin: CurrentAdmin,
):
    """Update the status of a FOIA request."""
    foia = db.query(FOIARequest).filter(FOIARequest.id == foia_id).first()
    
    if not foia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FOIA request not found"
        )
    
    foia.status = status_data.status
    
    if status_data.tracking_number:
        foia.tracking_number = status_data.tracking_number
    if status_data.response_notes:
        foia.response_notes = status_data.response_notes
    if status_data.denial_reason:
        foia.denial_reason = status_data.denial_reason
    if status_data.actual_response_date:
        foia.actual_response_date = status_data.actual_response_date
    
    # Set follow-up date based on status
    if status_data.status == FOIAStatus.SUBMITTED:
        # Set request date to today if not set
        if not foia.request_date:
            foia.request_date = date.today()
            foia.expected_response_date = calculate_expected_response_date(foia.request_date)
        foia.follow_up_date = foia.expected_response_date
    elif status_data.status in [FOIAStatus.COMPLETED, FOIAStatus.DENIED, FOIAStatus.WITHDRAWN]:
        foia.follow_up_date = None
    
    db.commit()
    db.refresh(foia)
    
    return FOIARequestResponse.model_validate(foia)


@router.delete("/{foia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_foia_request(
    foia_id: int,
    db: DbSession,
    admin: CurrentAdmin,
):
    """Delete a FOIA request."""
    foia = db.query(FOIARequest).filter(FOIARequest.id == foia_id).first()
    
    if not foia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FOIA request not found"
        )
    
    db.delete(foia)
    db.commit()
