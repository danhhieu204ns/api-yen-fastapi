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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    birthdate = Column(Date, nullable=False)
    address = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)


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

    # user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    # inviter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # info = relationship("User", foreign_keys=[user_id])


class Publisher(Base):
    __tablename__ = "publishers"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class Bookgroup(Base):
    __tablename__ = "bookgroups"

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
    

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    bookgroup_id = Column(Integer, ForeignKey("bookgroups.id", ondelete="CASCADE"), nullable=False)

    bookgroup = relationship("Bookgroup", foreign_keys=[bookgroup_id])
    

class Borrow(Base):
    __tablename__ = "borrows"

    id = Column(Integer, primary_key=True, nullable=False)
    duration = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    bookgroup_id = Column(Integer, ForeignKey("bookgroups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    staff_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    bookgroup = relationship("Bookgroup", foreign_keys=[bookgroup_id])
    user = relationship("User", foreign_keys=[user_id])
    staff = relationship("User", foreign_keys=[staff_id])

    