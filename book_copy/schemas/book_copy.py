from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class BookCopyBase(BaseModel):
    status: Optional[str] = None
    
    book_id: int
    bookshelf_id: int


class BookCopyCreate(BookCopyBase):
    pass


class BookCopyUpdate(BookCopyBase):
    pass


class BookCopyResponse(BookCopyBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class BookCopyPageableResponse(BaseModel):
    book_copies: list[BookCopyResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True

class BookCopyImport(BaseModel):
    book_copies: list[BookCopyBase]

    class Config:
        from_attributes = True