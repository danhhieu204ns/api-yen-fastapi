from fastapi import status, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Optional
from .. import schemas, models, utils
import math


def get_borrow_all(db: Session, 
                   limit: int, 
                   skip: int, 
                   search: Optional[str] | None):
    
    borrows = utils.query_borrow_all(db, limit, skip, search).all()
    return borrows


def get_borrow_by_id(borrow_id: int, 
                     db: Session):
    
    borrow = utils.query_borrow_by_id(db, borrow_id).first()
    if not borrow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found borrow")
    
    return borrow


def get_borrow_by_user(
        db: Session,
        current_user
    ):
    
    borrows = db.query(models.Borrow).filter(models.Borrow.user_id == current_user.id).all()
    
    return borrows


def get_borrow_with_user_id(
        user_id: int,
        db: Session,
        current_user
    ):
    
    borrows = db.query(models.Borrow).filter(
        models.Borrow.user_id == user_id,
        or_(
            models.Borrow.status == "Đang mượn",
            models.Borrow.status == "Đã quá hạn"
        )
    ).all()
    
    return borrows


def get_borrow_with_user_id_and_book_id(
        return_info: schemas.BorrowReturnInfo, 
        db: Session,
        current_user
    ):
    
    borrows = db.query(models.Borrow).filter(
        models.Borrow.user_id == return_info.user_id,
        models.Borrow.book_id == return_info.book_id,
        or_(
            models.Borrow.status == "Đang mượn",
            models.Borrow.status == "Đã quá hạn"
        )
    ).first()
    return borrows


def get_borrow_pageable(page: int, 
                        page_size: int, 
                        db: Session):
     
    total_count = db.query(models.Borrow).count()
    total_pages = math.ceil(total_count / page_size)
    offset = (page - 1) * page_size
    borrows = db.query(models.Borrow).offset(offset).limit(page_size).all()

    borrow_pageable_res = schemas.BorrowPageableResponse(
        borrows=borrows,
        total_pages=total_pages,
        total_data=total_count
    )

    return borrow_pageable_res


def create_borrow_by_user(
    new_borrow: schemas.BorrowCreate, 
    db: Session, 
    current_user
):
    exitsed_borrow = db.query(models.Borrow).filter(
        models.Borrow.user_id == new_borrow.user_id,
        models.Borrow.book_id == new_borrow.book_id,
        or_(
            models.Borrow.status == "Đang mượn",
            models.Borrow.status == "Đã quá hạn",
            models.Borrow.status == "Đã chờ xác nhận"
        )
    ).first()

    if exitsed_borrow:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Bạn đã có đơn mượn cuốn sách này rồi!!")

    borrow = models.Borrow(**new_borrow.dict(), 
                           status = "Đang chờ xác nhận")
    db.add(borrow)
    db.commit()
    
    return borrow


def create_borrow_by_admin(new_borrow: schemas.BorrowResponse, 
                  db: Session, 
                  current_user):
 
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")

    exitsed_borrow = db.query(models.Borrow).filter(
        models.Borrow.user_id == new_borrow.user_id,
        models.Borrow.book_id == new_borrow.book_id,
        or_(
            models.Borrow.status == "Đang mượn",
            models.Borrow.status == "Đã quá hạn",
            models.Borrow.status == "Đã chờ xác nhận"
        )
    ).first()

    if exitsed_borrow:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Người dùng đã có đơn mượn cuốn sách này rồi!!")

    borrow = models.Borrow(**new_borrow.dict(), 
                           status = "Đang mượn")
    db.add(borrow)
    db.commit()
    
    return borrow


def update_borrow(borrow_id: int,
                  new_borrow: schemas.BorrowUpdate, 
                  db: Session, 
                  current_user):
    
    borrow_query = utils.query_borrow_by_id(db, borrow_id)
     
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    borrow_query.update(new_borrow.dict(), synchronize_session=False)
    db.commit()
    
    return borrow_query.first()


def cancel_borrow_by_user(
        borrow_id: int, 
        db: Session,
        current_user
):
    borrow = db.query(models.Borrow).filter(models.Borrow.id == borrow_id)

    borrow.update(
        {"status": "Đã hủy"},
        synchronize_session=False
    )
    db.commit()

    return borrow.first()


def return_borrow_by_user(
        borrow_id: int, 
        db: Session,
        current_user
):
    borrow = db.query(models.Borrow).filter(models.Borrow.id == borrow_id)

    borrow.update(
        {"status": "Đã trả"},
        synchronize_session=False
    )
    db.commit()

    return borrow.first()


def delete_borrow(borrow_id: int, 
                  db: Session, 
                  current_user):
    borrow_query = utils.query_borrow_by_id(db, borrow_id)
     
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    borrow_query.delete(synchronize_session=False)
    db.commit()
    
    return {"message": "Delete borrow succesfull"}


def delete_many_borrow(borrow_ids: schemas.DeleteMany, 
                       db: Session, 
                       current_user):
    
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Không có quyền thực hiện thao tác này")

    borrow_query = db.query(models.Borrow).filter(models.Borrow.id.in_(borrow_ids.list_id))

    if borrow_query.count() == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Không tìm thấy borrow với các ID đã cung cấp")

    borrow_query.delete(synchronize_session=False)
    db.commit()

    return {"message": "Xóa danh sách borrow thành công"}
