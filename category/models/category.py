from sqlalchemy import Column, String, Integer, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Category(Base): # the loai
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    age_limit = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    books = relationship("Book", back_populates="category")