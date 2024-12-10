from sqlalchemy import Column, String, Integer, text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Bookshelf(Base):
    __tablename__ = "bookshelfs"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    book_copies = relationship("BookCopy", back_populates="bookshelf")
