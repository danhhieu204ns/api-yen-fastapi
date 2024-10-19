from fastapi import status, HTTPException, Depends, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from .. import models, schemas, utils
from ..database import get_db
import math, os


def get_genre_all(db: Session, 
                  limit: int, 
                  skip: int, 
                  search: Optional[str]):
    
    genres = utils.query_genre_all(db, limit, skip, search).all()

    return genres


def get_genre_by_id(genre_id: int, 
                    db: Session):
    
    genre = utils.query_genre_by_id(db, genre_id).first()
    if not genre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found genre")
    
    return genre


def get_genre_pageable(page: int, 
                        page_size: int, 
                        db: Session):
     
    total_count = db.query(models.Genre).count()  # Dùng count() để lấy số lượng mục
    total_pages = math.ceil(total_count / page_size)
    offset = (page - 1) * page_size
    genres = db.query(models.Genre).offset(offset).limit(page_size).all()

    return {
        "genres": genres, 
        "total_pages": total_pages,
        "total_data": total_count
    }


def create_genre(new_genre: schemas.GenreCreate, 
                 db: Session, 
                 current_user):

    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    print(new_genre)
    genre = models.Genre(**new_genre.dict())
    db.add(genre)
    db.commit()
    
    return genre


def update_genre(genre_id: int,
                     new_genre: schemas.GenreUpdate, 
                     db: Session, 
                     current_user):
    genre_query = utils.query_genre_by_id(db, genre_id)
    if not genre_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found genre")
     
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    genre_query.update(new_genre.dict(), synchronize_session=False)
    db.commit()
    
    return genre_query.first()


def delete_genre(genre_id: int, 
                 db: Session, 
                 current_user):
    genre_query = utils.query_genre_by_id(db, genre_id)
    if not genre_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found genre")
     
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    genre_query.delete(synchronize_session=False)
    db.commit()
    
    return {"message": "Delete genre succesfull"}


def delete_many_genre(genre_ids: schemas.DeleteMany, 
                      db: Session, 
                      current_user):
    
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Không có quyền thực hiện thao tác này")

    genre_query = db.query(models.Genre).filter(models.Genre.id.in_(genre_ids.list_id))

    if genre_query.count() == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Không tìm thấy thể loại với các ID đã cung cấp")

    # Xóa các tác giả
    genre_query.delete(synchronize_session=False)
    db.commit()

    return {"message": "Xóa danh sách thể loại thành công"}


# async def upload_file(file: UploadFile,
#                       db: Session, 
#                       current_user):

#     UPLOAD_DIRECTORY = os.path.abspath("./files/")
#     if not os.path.exists(UPLOAD_DIRECTORY):
#         os.makedirs(UPLOAD_DIRECTORY)

#     file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
#     with open(file_location, "wb") as f:
#         f.write(await file.read())

#     new_file = models.File(path=file_location, 
#                            user_id=current_user.id, 
#                            name=file.filename)
#     db.add(new_file)
#     db.commit()

#     return {"filename": file.filename, 
#             "status": "accepted!"}


# def download_file(db: Session = Depends(get_db), 
#                   current_user = Depends(oauth2.get_current_user)):

#     file = db.query(models.File).first()
#     if not file:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
#                             detail="Not found!")
    
#     return FileResponse(file.path)