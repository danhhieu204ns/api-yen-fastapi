from sqlalchemy import Column, String, Integer, text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    pages = Column(Integer, nullable=True)
    language = Column(String, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    author_id = Column(Integer, ForeignKey("authors.id", ondelete="SET NULL"), nullable=True)
    publisher_id = Column(Integer, ForeignKey("publishers.id", ondelete="SET NULL"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    author = relationship("Author", back_populates="books")
    publisher = relationship("Publisher", back_populates="books")
    category = relationship("Category", back_populates="books")

    book_copies = relationship("BookCopy", back_populates="book", uselist=True)
