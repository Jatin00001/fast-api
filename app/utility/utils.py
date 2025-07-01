"""
Utility functions for the FastAPI application
"""

import re
import unicodedata
from typing import Optional

def secure_filename(filename: str) -> str:
    """
    Secure a filename by removing or replacing unsafe characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Secured filename safe for filesystem use
    """
    if not filename:
        return "unnamed_file"
    
    # Normalize unicode characters
    filename = unicodedata.normalize('NFKD', filename)
    
    # Remove or replace unsafe characters
    filename = re.sub(r'[^\w\s\-_\.]', '', filename)
    
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    
    # Remove multiple consecutive dots, underscores, or hyphens
    filename = re.sub(r'[._-]+', lambda m: m.group(0)[0], filename)
    
    # Ensure filename is not empty and has reasonable length
    if not filename or filename == '.':
        filename = "unnamed_file"
    
    # Limit filename length (filesystem limit is usually 255)
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_length = 255 - len(ext) - 1 if ext else 255
        filename = name[:max_name_length] + ('.' + ext if ext else '')
    
    return filename

def generate_slug(text: str) -> str:
    """
    Generate a URL-friendly slug from text.
    
    Args:
        text: Text to convert to slug
        
    Returns:
        URL-friendly slug
    """
    if not text:
        return ""
    
    # Convert to lowercase and normalize unicode
    slug = unicodedata.normalize('NFKD', text.lower())
    
    # Remove non-alphanumeric characters except spaces and hyphens
    slug = re.sub(r'[^\w\s\-]', '', slug)
    
    # Replace spaces and multiple hyphens with single hyphen
    slug = re.sub(r'[\s\-]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug

# Helper functions that might be useful for future features
def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted file size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def sanitize_html(text: str) -> str:
    """
    Basic HTML sanitization by removing HTML tags.
    
    Args:
        text: Text that may contain HTML
        
    Returns:
        Text with HTML tags removed
    """
    if not text:
        return ""
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # Decode common HTML entities
    html_entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' '
    }
    
    for entity, char in html_entities.items():
        clean_text = clean_text.replace(entity, char)
    
    return clean_text.strip()

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length with optional suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length of result
        suffix: Suffix to add if text is truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def extract_coordinates(location_string: str) -> Optional[tuple]:
    """
    Extract latitude and longitude from a location string.
    
    Args:
        location_string: String containing coordinates
        
    Returns:
        Tuple of (latitude, longitude) or None if not found
    """
    if not location_string:
        return None
    
    # Pattern to match various coordinate formats
    patterns = [
        r'(-?\d+\.?\d*),\s*(-?\d+\.?\d*)',  # "lat,lng" or "lat, lng"
        r'lat:\s*(-?\d+\.?\d*),?\s*lng:\s*(-?\d+\.?\d*)',  # "lat: x, lng: y"
        r'latitude:\s*(-?\d+\.?\d*),?\s*longitude:\s*(-?\d+\.?\d*)',  # "latitude: x, longitude: y"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, location_string, re.IGNORECASE)
        if match:
            try:
                lat, lng = float(match.group(1)), float(match.group(2))
                # Validate coordinate ranges
                if -90 <= lat <= 90 and -180 <= lng <= 180:
                    return (lat, lng)
            except ValueError:
                continue
    
    return None

def generate_unique_identifier(prefix: str = "", length: int = 8) -> str:
    """
    Generate a unique identifier with optional prefix.
    
    Args:
        prefix: Optional prefix for the identifier
        length: Length of the random part
        
    Returns:
        Unique identifier string
    """
    import uuid
    
    # Generate random part
    random_part = str(uuid.uuid4()).replace('-', '')[:length]
    
    if prefix:
        return f"{prefix}_{random_part}"
    
    return random_part
