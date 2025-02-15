from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class BorrowBase(BaseModel):
    user_id: int
    book_copy_id: int
    staff_id: Optional[int] = None
    duration: Optional[int] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


class BorrowCreate(BorrowBase):
    pass


class BorrowUpdate(BorrowBase):
    user_id: Optional[int] = None
    book_copy_id: Optional[int] = None


class BorrowResponse(BorrowBase):
    id: int
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