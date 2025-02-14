from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class PublisherBase(BaseModel):
    name: str
    phone_number: Optional[str]
    address: Optional[str]
    email: Optional[str]


class PublisherCreate(PublisherBase):
    pass


class PublisherUpdate(PublisherBase):
    name: Optional[str] = None
    

class PublisherResponse(PublisherBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ListPublisherResponse(BaseModel):
    publishers: list[PublisherResponse]
    total_data: int

    class Config:
        from_attributes = True


class PublisherPageableResponse(BaseModel):
    publishers: list[PublisherResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True


class PublisherSearch(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


class DeleteMany(BaseModel):
    list_id: list[int]

    class Config:
        from_attributes = True