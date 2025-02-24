from datetime import date, datetime
from pydantic import BaseModel
from typing import List, Optional

from book.schemas.book import BookBase
from bookshelf.schemas.bookshelf import BookshelfBase


class BookCopyBase(BaseModel):
    status: str
    book_id: int
    bookshelf_id: Optional[int] = None

    class Config:
        from_attributes = True


class BookCopyCreate(BookCopyBase):
    pass


class BookCopyUpdate(BaseModel):
    status: Optional[str] = None
    bookshelf_id: Optional[int] = None


class BookCopyResponse(BaseModel):
    id: int
    book: BookBase
    bookshelf: Optional[BookshelfBase] = None
    status: str

    class Config:
        from_attributes = True


class ListBookCopyResponse(BaseModel):
    book_copies: List[BookCopyResponse]
    total_data: int

    class Config:
        from_attributes = True


class BookCopyPageableResponse(BaseModel):
    book_copies: List[BookCopyResponse]
    total_data: int
    total_pages: Optional[int] = None

    class Config:
        from_attributes = True


class BookCopySearch(BaseModel):
    status: Optional[str] = None


class DeleteMany(BaseModel):
    ids: List[int]