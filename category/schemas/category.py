from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class CategoryBase(BaseModel):
    name: str
    age_limit: Optional[int]
    description: Optional[str]


class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CategoryPageableResponse(BaseModel):
    categories: list[CategoryResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True


class CategoryImport(BaseModel):
    categories: list[CategoryBase]

    class Config:
        from_attributes = True