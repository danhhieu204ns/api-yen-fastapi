from sqlalchemy import Column, String, Integer, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    birthdate = Column(String, nullable=True)
    address = Column(String, nullable=True)
    pen_name = Column(String, nullable=True)
    biography = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    books = relationship("Book", back_populates="author", uselist=True)