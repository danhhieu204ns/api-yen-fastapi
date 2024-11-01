from passlib.context import CryptContext
import re
from fastapi import HTTPException, status
from . import models


pwd_context = CryptContext(schemes=["bcrypt"])

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hassed_password):
    return pwd_context.verify(plain_password, hassed_password)

# Roles
def get_role_by_name(db, role_name):
    role = db.query(models.Role).filter(models.Role.name == role_name).first()
    return role

def get_role_by_id(db, role_id):
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    return role

def query_role_by_name(db, role_name):
    role_query = db.query(models.Role).filter(models.Role.name == role_name)
    return role_query

def query_role_by_id(db, role_id):
    role_query = db.query(models.Role).filter(models.Role.id == role_id)
    return role_query


# Users
def get_user_by_id(db, user_id):
    user = db.query(models.UserInfo).filter(models.UserInfo.id == user_id).first()
    return user

def get_admin_by_id(db, user_id):
    admin = db.query(models.UserInfo).filter(models.UserInfo.id == user_id, 
                                         models.UserInfo.role_id == get_role_by_name(db, models, "admin")).first()
    return admin


# Authors
def query_author_by_id(db, author_id):
    author_query = db.query(models.Author).filter(models.Author.id == author_id)
    return author_query

def query_author_all(db):
    author_query = db.query(models.Author)
    return author_query


# Publishers
def query_publisher_by_id(db, publisher_id):
    publisher_query = db.query(models.Publisher).filter(models.Publisher.id == publisher_id)
    return publisher_query

def query_publisher_all(db, limit, skip, search):
    publisher_query = db.query(models.Publisher).limit(limit).offset(skip)
    return publisher_query


# Genres
def query_genre_by_id(db, genre_id):
    genre_query = db.query(models.Genre).filter(models.Genre.id == genre_id)
    return genre_query

def query_genre_all(db, limit, skip, search):
    genre_query = db.query(models.Genre).limit(limit).offset(skip)
    return genre_query


# Books
def query_book_by_id(db, book_id):
    book_query = db.query(models.Book).filter(models.Book.id == book_id)
    return book_query

def query_book_all(db):
    book_query = db.query(models.Book)
    return book_query



# Borrow
def query_borrow_by_id(db, borrow_id):
    borrow_query = db.query(models.Borrow).filter(models.Borrow.id == borrow_id)
    return borrow_query

def query_borrow_all(db, limit, skip, search):
    borrow_query = db.query(models.Borrow).limit(limit).offset(skip)
    return borrow_query




def validate_user_credentials(username, password):
    if username:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Tên đăng nhập đã tồn tại."
        )
    
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Mật khẩu phải có ít nhất 8 kí tự."
        )
    
    if not re.search(r'[A-Z]', password):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Mật khẩu phải có ít nhất 1 kí tự in hoa."
        )
    
    if not re.search(r'[a-z]', password):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Mật khẩu phải có ít nhất 1 kí tự in thường."
        )
    
    if not re.search(r'[0-9]', password):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Mật khẩu phải có ít nhất 1 chữ số."
        )
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Mật khẩu phải có ít nhất 1 kí tự đặc biệt."
        )


