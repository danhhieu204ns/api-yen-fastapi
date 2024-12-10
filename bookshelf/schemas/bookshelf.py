from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class BookshelfBase(BaseModel):
    name: str
    status: Optional[str] = None


class BookshelfCreate(BookshelfBase):
    pass


class BookshelfUpdate(BaseModel):
    status: Optional[str] = None


class BookshelfResponse(BookshelfBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class BookshelfPageableResponse(BaseModel):
    bookshelfs: list[BookshelfResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True
        

class BookshelfImport(BaseModel):
    bookshelfs: list[BookshelfBase]

    class Config:
        from_attributes = True