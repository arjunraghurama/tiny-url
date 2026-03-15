from pydantic import BaseModel, HttpUrl
from datetime import datetime


class ShortenRequest(BaseModel):
    """Request body for creating a shortened URL."""
    url: HttpUrl


class ShortenResponse(BaseModel):
    """Response after successfully creating a short URL."""
    short_code: str
    short_url: str
    original_url: str
    created_at: datetime


class URLStats(BaseModel):
    """Statistics for a shortened URL."""
    short_code: str
    short_url: str
    original_url: str
    clicks: int
    created_at: datetime
    is_active: bool


class URLListItem(BaseModel):
    """Item in the recent URLs list."""
    short_code: str
    short_url: str
    original_url: str
    clicks: int
    created_at: datetime
