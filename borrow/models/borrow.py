from sqlalchemy import Column, String, Integer, text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Borrow(Base):
    __tablename__ = "borrows"

    id = Column(Integer, primary_key=True, nullable=False)
    duration = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    book_copy_id = Column(Integer, ForeignKey("book_copies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_infos.id", ondelete="CASCADE"), nullable=False)
    staff_id = Column(Integer, ForeignKey("user_infos.id", ondelete="CASCADE"), nullable=True)

    book_copy = relationship("BookCopy", back_populates="borrows")
    user = relationship("UserInfo", back_populates="borrows", foreign_keys=[user_id])
    staff = relationship("UserInfo", back_populates="borrows", foreign_keys=[staff_id])