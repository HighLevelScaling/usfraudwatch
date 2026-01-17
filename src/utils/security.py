import re
from typing import Optional


def generate_slug(title: str) -> str:
    """Generate a URL-friendly slug from a title."""
    # Convert to lowercase
    slug = title.lower()
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    # Remove consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    return slug


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe storage."""
    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')
    # Remove special characters except dot, hyphen, underscore
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return filename


def mask_email(email: str) -> str:
    """Mask an email address for display (e.g., j***@example.com)."""
    if '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked_local = local[0] + '***'
    else:
        masked_local = local[0] + '***' + local[-1]
    
    return f"{masked_local}@{domain}"
