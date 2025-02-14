from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class AuthorBase(BaseModel):
    name: str
    birthdate: Optional[str]
    address: Optional[str]
    pen_name: Optional[str]
    biography: Optional[str]


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(AuthorBase):
    name: Optional[str] = None


class AuthorResponse(AuthorBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ListAuthorResponse(BaseModel):
    authors: list[AuthorResponse]
    total_data: int

    class Config:
        from_attributes = True


class AuthorPageableResponse(BaseModel):
    authors: list[AuthorResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True


class AuthorImport(BaseModel):
    authors: list[AuthorBase]

    class Config:
        from_attributes = True


class AuthorSearch(AuthorBase):
    name: Optional[str] = None

    class Config:
        from_attributes = True