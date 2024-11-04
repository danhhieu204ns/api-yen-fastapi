from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from datetime import datetime



class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class UserAuth(Base):
    __tablename__ = "user_auths"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    user_info = relationship("UserInfo", back_populates="user_auth", uselist=False)


class UserInfo(Base):
    __tablename__ = "user_infos"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    birthdate = Column(Date, nullable=False)
    address = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    status = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    user_auth_id = Column(Integer, ForeignKey("user_auths.id", ondelete="CASCADE"), nullable=False)

    role = relationship("Role", foreign_keys=[role_id])
    user_auth = relationship("UserAuth", back_populates="user_info")


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    birthdate = Column(Date, nullable=False)
    address = Column(String, nullable=False)
    pen_name = Column(String, nullable=False)
    biography = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class Genre(Base): # the loai
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    age_limit = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class Publisher(Base):
    __tablename__ = "publishers"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    content = Column(String, nullable=False)  
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    author_id = Column(Integer, ForeignKey("authors.id", ondelete="CASCADE"), nullable=True)
    publisher_id = Column(Integer, ForeignKey("publishers.id", ondelete="CASCADE"), nullable=False)
    genre_id = Column(Integer, ForeignKey("genres.id", ondelete="CASCADE"), nullable=False)

    author = relationship("Author", foreign_keys=[author_id])
    publisher = relationship("Publisher", foreign_keys=[publisher_id])
    genre = relationship("Genre", foreign_keys=[genre_id])
    
    

class Borrow(Base):
    __tablename__ = "borrows"

    id = Column(Integer, primary_key=True, nullable=False)
    duration = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_infos.id", ondelete="CASCADE"), nullable=False)
    staff_id = Column(Integer, ForeignKey("user_infos.id", ondelete="CASCADE"), nullable=True)

    book = relationship("Book", foreign_keys=[book_id])
    user = relationship("UserInfo", foreign_keys=[user_id])
    staff = relationship("UserInfo", foreign_keys=[staff_id])

    