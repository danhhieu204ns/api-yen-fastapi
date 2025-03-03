from sqlalchemy import Column, String, Integer, text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class BookCopy(Base):
    __tablename__ = "book_copies"

    id = Column(Integer, primary_key=True, nullable=False)
    status = Column(String, nullable=False, server_default=text("'AVAILABLE'"))

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    bookshelf_id = Column(Integer, ForeignKey("bookshelfs.id", ondelete="SET NULL"), nullable=True)

    book = relationship("Book", back_populates="book_copies")
    bookshelf = relationship("Bookshelf", back_populates="book_copies")
    borrows = relationship("Borrow", back_populates="book_copy")