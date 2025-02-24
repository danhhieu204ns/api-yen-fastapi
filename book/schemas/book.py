from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class AuthorBase(BaseModel):
    name: str
    id: int

    class Config:
        from_attributes = True


class PublisherBase(BaseModel):
    name: str
    id: int

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    id: int

    class Config:
        from_attributes = True


class BookBase(BaseModel):
    name: str
    status: Optional[str] = None
    summary: Optional[str] = None
    pages: Optional[int] = None
    language: Optional[str] = None


class BookCreate(BookBase):
    name: Optional[str] = None
    author_id: Optional[int] = None
    publisher_id: Optional[int] = None
    category_id: Optional[int] = None


class BookUpdate(BookBase):
    name: Optional[str] = None
    author_id: Optional[int] = None
    publisher_id: Optional[int] = None
    category_id: Optional[int] = None


class BookResponse(BookBase):
    id: int
    author: Optional[AuthorBase] = None
    publisher: Optional[PublisherBase] = None
    category: Optional[CategoryBase] = None
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


class BookNameResponse(BaseModel):
    name: str
    id: int

    class Config:
        from_attributes = True


class ListBookNameResponse(BaseModel):
    books: list[BookNameResponse]

    class Config:
        from_attributes = True
        