from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class StatsResponse(BaseModel):
    total_books: int
    total_borrows: int
    borrowed_books: int
    active_users: int

class TopBookItem(BaseModel):
    name: str
    count: int

class TopBooksResponse(BaseModel):
    top_books: List[TopBookItem]

class MonthlyBorrowItem(BaseModel):
    month: str
    count: int

class MonthlyBorrowsResponse(BaseModel):
    monthly_borrows: List[MonthlyBorrowItem]

class CategoryStatsItem(BaseModel):
    category: str
    count: int

class CategoryStatsResponse(BaseModel):
    categories: list[CategoryStatsItem]

class BookStatusItem(BaseModel):
    status: str
    count: int

class BookStatusResponse(BaseModel):
    statuses: list[BookStatusItem]