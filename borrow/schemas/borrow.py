from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional

from book_copy.schemas.book_copy import BookCopyResponse


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True


class BorrowBase(BaseModel):
    user_id: Optional[int] = None
    book_id: int
    staff_id: Optional[int] = None
    borrow_date: Optional[date] = None
    duration: Optional[int] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


class BorrowCreate(BorrowBase):
    pass


class BorrowUpdate(BaseModel):
    duration: Optional[int] = None
    status: Optional[str] = None


class BorrowResponse(BaseModel):
    id: int
    user: UserResponse
    book_copy: BookCopyResponse
    staff: Optional[UserResponse] = None
    borrow_date: Optional[date] = None
    duration: Optional[int] = None
    status: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ListBorrowResponse(BaseModel):
    borrows: list[BorrowResponse]
    total_data: int

    class Config:
        from_attributes = True


class BorrowPageableResponse(BaseModel):
    borrows: list[BorrowResponse]
    
    total_pages: int
    total_data: int

    class Config:
        from_attributes = True


class BorrowSearch(BaseModel):
    user_id: Optional[int] = None
    book_copy_id: Optional[int] = None
    staff_id: Optional[int] = None
    status: Optional[str] = None
    duration: Optional[int] = None

    class Config:
        from_attributes = True


class DeleteMany(BaseModel):
    ids: list[int]

    class Config:
        from_attributes = True