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


class ListCategoryResponse(BaseModel):
    categories: list[CategoryResponse]
    total_data: int

    class Config:
        from_attributes = True


class CategoryPageableResponse(BaseModel):
    categories: list[CategoryResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True


class CategorySearch(BaseModel):
    name: Optional[str] = None
    age_limit: Optional[int] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class CategoryDelete(BaseModel):
    list_id: list[int]

    class Config:
        from_attributes = True



class CategoryName(BaseModel):
    name: str
    id: int

    class Config:
        from_attributes = True


class ListCategoryNameResponse(BaseModel):
    categories: list[CategoryName]

    class Config:
        from_attributes = True