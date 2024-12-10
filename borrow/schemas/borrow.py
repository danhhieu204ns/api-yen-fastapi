from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class BorrowBase(BaseModel):
    user_id: int
    book_copy_id: int
    staff_id: Optional[int]
    duration: Optional[int]
    status: Optional[str]

    class Config:
        from_attributes = True


class BorrowCreate(BorrowBase):
    pass


class BorrowUpdate(BorrowBase):
    pass


class BorrowResponse(BorrowBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class BorrowPageableResponse(BaseModel):
    borrows: list[BorrowResponse]
    
    total_pages: int
    total_data: int

    class Config:
        from_attributes = True


class BorrowImport(BaseModel):
    borrows: list[BorrowCreate]

    class Config:
        from_attributes = True