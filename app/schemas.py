from fastapi import Form
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class DeleteMany(BaseModel):
    list_id: list[int]


# Token
class Token(BaseModel):
    access_token: str
    token_type: str


class Tokendata(BaseModel):
    id: Optional[int] = None



# Role
class RoleCreate(BaseModel):
    name: str


class RoleAssign(BaseModel):
    role_name: str
    user_id: int


class RoleResponse(BaseModel):
    name: str

    class Config:
        from_attributes = True


class RoleDelete(RoleCreate):
    pass

class UserAuthResponse(BaseModel):
    username: str

    class Config:
        from_attributes = True


# User
class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    birthdate: date
    address: str
    phone_number: str
    image: str


class UserResponse(BaseModel):
    id: int
    name: str
    birthdate: date
    address: str
    phone_number: str
    status: bool
    created_at: datetime

    role: RoleResponse
    user_auth: UserAuthResponse
    
    class Config:
        from_attributes = True


class UserPageableResponse(BaseModel):
    users: list[UserResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    birthdate: Optional[date] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None


class UserRePwd(BaseModel):
    username: str


class UserUpdatePwd(BaseModel):
    password: str


# Author
class AuthorCreate(BaseModel):
    name: str
    birthdate: date
    address: str
    pen_name: str
    biography: str


class AuthorResponse(BaseModel):
    id: int
    name: str
    birthdate: date
    address: str
    pen_name: str
    biography: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuthorUpdate(BaseModel):
    name: Optional[str] = None
    birthdate: Optional[date] = None
    address: Optional[str] = None
    pen_name: Optional[str] = None
    biography: Optional[str] = None



# Genre
class GenreCreate(BaseModel):
    name: str
    age_limit: int
    description: str


class GenreResponse(BaseModel):
    id: int
    name: str
    age_limit: int
    description: str
    
    class Config:
        from_attributes = True


class GenreUpdate(BaseModel):
    name: Optional[str] = None
    age_limit: Optional[int] = None
    description: Optional[str] = None


# Publisher
class PublisherCreate(BaseModel):
    name: str
    phone_number: str
    address: str
    email: str


class PublisherUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    

class PublisherResponse(BaseModel):
    id: int
    name: str
    phone_number: str
    address: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True



# Book
class BookCreate(BaseModel):
    name: str
    status: str
    content: str
    author_id: int
    publisher_id: int
    genre_id: int


class BookResponse(BaseModel):
    id: int
    name: str
    status: str
    content: str
    created_at: datetime

    author: AuthorResponse
    publisher: PublisherResponse
    genre: GenreResponse

    class Config:
        from_attributes = True


class BookPageableResponse(BaseModel):
    books: list[BookResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True


class BookUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    content: Optional[str] = None
    author_id: Optional[int] = None
    publisher_id: Optional[int] = None
    genre_id: Optional[int] = None



# Borrow
class BorrowCreate(BaseModel):
    book_id: int
    user_id: int
    staff_id: Optional[int] = None
    duration: int


class BorrowUpdate(BaseModel):
    book_id: Optional[int] = None
    user_id: Optional[int] = None
    staff_id: Optional[int] = None
    duration: Optional[int] = None
    status: Optional[str] = None


class BorrowReturnInfo(BaseModel):
    book_id: int
    user_id: int


class BorrowResponse(BaseModel):
    id: int
    duration: int
    status: str
    book: BookResponse
    user: UserResponse
    staff: Optional[UserResponse]
    created_at: datetime

    class Config:
        from_attributes = True


class BorrowPageableResponse(BaseModel):
    borrows: list[BorrowResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True

