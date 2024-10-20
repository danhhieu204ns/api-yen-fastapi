from fastapi import status, HTTPException
from .. import schemas, models, utils
from sqlalchemy.orm import Session
import math


def get_author_by_id(author_id: int, 
                     db: Session):
    
    author = utils.query_author_by_id(db, author_id).first()
    
    return author


def get_author_all(db: Session):
    
    authors = utils.query_author_all(db).all()
    
    return authors


def get_author_pageable(page: int, 
                        page_size: int, 
                        db: Session):
     
    total_count = db.query(models.Author).count()  # Dùng count() để lấy số lượng mục
    total_pages = math.ceil(total_count / page_size)
    offset = (page - 1) * page_size
    authors = db.query(models.Author).offset(offset).limit(page_size).all()

    return {
        "authors": authors, 
        "total_pages": total_pages,
        "total_data": total_count
    }

def create_author(new_author: schemas.AuthorCreate, 
               db: Session, 
               current_user):
        
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    author = models.Author(**new_author.dict())
    db.add(author)
    db.commit()
    
    return author


def update_author(author_id: int,
                  new_author: schemas.AuthorCreate, 
                  db: Session, 
                  current_user):
    
    author_query = utils.query_author_by_id(db, author_id)
     
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    author_query.update(new_author.dict(), synchronize_session=False)
    db.commit()
    
    return author_query.first()


def delete_author(author_id: int, 
                  db: Session, 
                  current_user):
    
    author_query = utils.query_author_by_id(db, author_id)
     
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    author_query.delete(synchronize_session=False)
    db.commit()
    
    return {"message": "Delete author succesfull"}


def delete_many_author(author_ids: schemas.DeleteMany, 
                       db: Session, 
                       current_user):
    
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Không có quyền thực hiện thao tác này")

    author_query = db.query(models.Author).filter(models.Author.id.in_(author_ids.list_id))

    if author_query.count() == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Không tìm thấy tác giả với các ID đã cung cấp")

    author_query.delete(synchronize_session=False)
    db.commit()

    return {"message": "Xóa danh sách tác giả thành công"}