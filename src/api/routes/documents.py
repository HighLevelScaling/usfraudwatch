from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import RedirectResponse

from src.models import SourceDocument, DocumentType, SubscriptionTier
from src.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
    DocumentPaginatedResponse,
    UploadResponse,
)
from src.api.deps import DbSession, CurrentUser, CurrentUserOptional, CurrentAdmin
from src.services.storage_service import storage_service

router = APIRouter(prefix="/documents", tags=["documents"])

# Allowed file types
ALLOWED_TYPES = {
    "application/pdf": DocumentType.PDF,
    "image/jpeg": DocumentType.IMAGE,
    "image/png": DocumentType.IMAGE,
    "image/gif": DocumentType.IMAGE,
    "application/vnd.ms-excel": DocumentType.SPREADSHEET,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": DocumentType.SPREADSHEET,
    "text/csv": DocumentType.SPREADSHEET,
    "text/plain": DocumentType.TEXT,
    "video/mp4": DocumentType.VIDEO,
    "video/quicktime": DocumentType.VIDEO,
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@router.get("", response_model=DocumentPaginatedResponse)
async def list_documents(
    db: DbSession,
    user: CurrentUserOptional,
    document_type: Optional[DocumentType] = None,
    article_id: Optional[int] = None,
    foia_request_id: Optional[int] = None,
    public_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List documents with filtering."""
    query = db.query(SourceDocument)
    
    # Filter by access
    if not user or not user.is_admin:
        if public_only or not user:
            query = query.filter(SourceDocument.is_public == True)
        else:
            # Filter by tier
            accessible_tiers = [SubscriptionTier.FREE]
            if user.can_access_tier(SubscriptionTier.PATRIOT):
                accessible_tiers.append(SubscriptionTier.PATRIOT)
            if user.can_access_tier(SubscriptionTier.WATCHDOG):
                accessible_tiers.append(SubscriptionTier.WATCHDOG)
            if user.can_access_tier(SubscriptionTier.FOUNDER):
                accessible_tiers.append(SubscriptionTier.FOUNDER)
            
            query = query.filter(
                (SourceDocument.is_public == True) |
                (SourceDocument.tier_required.in_(accessible_tiers))
            )
    
    # Apply filters
    if document_type:
        query = query.filter(SourceDocument.document_type == document_type)
    if article_id:
        query = query.filter(SourceDocument.article_id == article_id)
    if foia_request_id:
        query = query.filter(SourceDocument.foia_request_id == foia_request_id)
    
    total = query.count()
    offset = (page - 1) * page_size
    
    documents = (
        query
        .order_by(SourceDocument.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    
    pages = (total + page_size - 1) // page_size
    
    return DocumentPaginatedResponse(
        items=[DocumentListResponse.model_validate(d) for d in documents],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: DbSession,
    user: CurrentUserOptional,
):
    """Get a document by ID."""
    doc = db.query(SourceDocument).filter(SourceDocument.id == document_id).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check access
    if not doc.is_public:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        if not user.is_admin and not user.can_access_tier(doc.tier_required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Subscription tier '{doc.tier_required.value}' required"
            )
    
    response = DocumentResponse.model_validate(doc)
    response.download_url = storage_service.get_download_url(
        file_path=doc.file_path,
        s3_key=doc.s3_key,
    )
    
    return response


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    db: DbSession,
    user: CurrentUserOptional,
):
    """Get download URL for a document."""
    doc = db.query(SourceDocument).filter(SourceDocument.id == document_id).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check access
    if not doc.is_public:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        if not user.is_admin and not user.can_access_tier(doc.tier_required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Subscription tier '{doc.tier_required.value}' required"
            )
    
    download_url = storage_service.get_download_url(
        file_path=doc.file_path,
        s3_key=doc.s3_key,
    )
    
    if not download_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return RedirectResponse(url=download_url)


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    db: DbSession,
    admin: CurrentAdmin,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    is_public: bool = Form(False),
    tier_required: SubscriptionTier = Form(SubscriptionTier.FREE),
    source_name: Optional[str] = Form(None),
    source_url: Optional[str] = Form(None),
    article_id: Optional[int] = Form(None),
    foia_request_id: Optional[int] = Form(None),
):
    """Upload a new document (admin only)."""
    # Validate file type
    content_type = file.content_type or "application/octet-stream"
    document_type = ALLOWED_TYPES.get(content_type, DocumentType.OTHER)
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Upload file
    try:
        upload_result = await storage_service.upload_file(
            file=file.file,
            filename=file.filename or "document",
            content_type=content_type,
            folder="documents",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )
    
    # Create document record
    doc = SourceDocument(
        title=title,
        description=description,
        document_type=document_type,
        file_path=upload_result.get("file_path"),
        s3_key=upload_result.get("s3_key"),
        file_size=upload_result.get("file_size"),
        mime_type=content_type,
        is_public=is_public,
        tier_required=tier_required,
        source_name=source_name,
        source_url=source_url,
        article_id=article_id,
        foia_request_id=foia_request_id,
    )
    
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    return UploadResponse(
        document_id=doc.id,
        title=doc.title,
        download_url=upload_result.get("url"),
    )


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    doc_data: DocumentUpdate,
    db: DbSession,
    admin: CurrentAdmin,
):
    """Update a document's metadata (admin only)."""
    doc = db.query(SourceDocument).filter(SourceDocument.id == document_id).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    update_data = doc_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doc, field, value)
    
    db.commit()
    db.refresh(doc)
    
    response = DocumentResponse.model_validate(doc)
    response.download_url = storage_service.get_download_url(
        file_path=doc.file_path,
        s3_key=doc.s3_key,
    )
    
    return response


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: DbSession,
    admin: CurrentAdmin,
):
    """Delete a document (admin only)."""
    doc = db.query(SourceDocument).filter(SourceDocument.id == document_id).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file from storage
    await storage_service.delete_file(
        file_path=doc.file_path,
        s3_key=doc.s3_key,
    )
    
    # Delete record
    db.delete(doc)
    db.commit()
