from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class BookCopyBase(BaseModel):
    status: Optional[str] = None


class BookCopyCreate(BookCopyBase):
    book_id: int
    bookshelf_id: Optional[int] = None


class BookCopyUpdate(BookCopyBase):
    pass


class BookCopyResponse(BookCopyBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ListBookCopyResponse(BaseModel):
    book_copies: list[BookCopyResponse]
    total_data: int

    class Config:
        from_attributes = True


class BookCopyPageableResponse(BaseModel):
    book_copies: list[BookCopyResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True


class BookCopySearch(BaseModel):
    status: Optional[str] = None


class DeleteMany(BaseModel):
    ids: list[int]