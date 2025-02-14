from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class BookBase(BaseModel):
    name: str
    status: Optional[str] = None
    summary: Optional[str] = None
    pages: Optional[int] = None
    language: Optional[str] = None


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    pass


class BookResponse(BookBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ListBookResponse(BaseModel):
    books: list[BookResponse]
    total_data: int

    class Config:
        from_attributes = True


class BookPageableResponse(BaseModel):
    books: list[BookResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True


class BookSearch(BookBase):
    name: Optional[str] = None


class DeleteMany(BaseModel):
    ids: list[int]