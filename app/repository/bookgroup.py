from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from .. import schemas, models, utils
import math



def get_bookgroup_all(db: Session, 
                      limit: int, 
                      skip: int, 
                      search: Optional[str] | None):
    
    bookgroups = utils.query_bookgroup_all(db, limit, skip, search).all()
    return bookgroups


def get_bookgroup_by_id(bookgroup_id: int, 
                    db: Session):
    
    bookgroup = utils.query_bookgroup_by_id(db, bookgroup_id).first()
    if not bookgroup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found bookgroup")
    
    return bookgroup


def get_bookgroup_pageable(page: int, 
                           page_size: int, 
                           db: Session):
     
    total_count = db.query(models.Bookgroup).count()
    total_pages = math.ceil(total_count / page_size)
    offset = (page - 1) * page_size
    bookgroups = db.query(models.Bookgroup).offset(offset).limit(page_size).all()

    bookgroup_pageable_res = schemas.BookgroupPageableResponse(
        bookgroups=bookgroups,
        total_pages=total_pages,
        total_data=total_count
    )

    return bookgroup_pageable_res


def create_bookgroup(new_bookgroup: schemas.BookgroupCreate, 
                 db: Session, 
                 current_user):
 
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")

    if not utils.query_author_by_id(db, new_bookgroup.author_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found author")
    
    if not utils.query_publisher_by_id(db, new_bookgroup.publisher_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found publisher")
    
    if not utils.query_genre_by_id(db, new_bookgroup.genre_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found genre")

    bookgroup = models.Bookgroup(**new_bookgroup.dict())
    db.add(bookgroup)
    db.commit()
    
    return bookgroup


def update_bookgroup(bookgroup_id: int,
                     new_bookgroup: schemas.BookgroupUpdate, 
                     db: Session, 
                     current_user):
    bookgroup_query = utils.query_bookgroup_by_id(db, bookgroup_id)
    if not bookgroup_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found bookgroup")
     
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    bookgroup_query.update(new_bookgroup.dict(), synchronize_session=False)
    db.commit()
    
    return bookgroup_query.first()


def delete_bookgroup(bookgroup_id: int, 
                 db: Session, 
                 current_user):
    bookgroup_query = utils.query_bookgroup_by_id(db, bookgroup_id)
    if not bookgroup_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found bookgroup")
     
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    bookgroup_query.delete(synchronize_session=False)
    db.commit()
    
    return {"message": "Delete bookgroup succesfull"}


def delete_many_bookgroup(bookgroup_ids: schemas.DeleteMany, 
                       db: Session, 
                       current_user):
    
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Không có quyền thực hiện thao tác này")

    bookgroup_query = db.query(models.Bookgroup).filter(models.Bookgroup.id.in_(bookgroup_ids.list_id))

    if bookgroup_query.count() == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Không tìm thấy bookgroup với các ID đã cung cấp")

    bookgroup_query.delete(synchronize_session=False)
    db.commit()

    return {"message": "Xóa danh sách bookgroup thành công"}
