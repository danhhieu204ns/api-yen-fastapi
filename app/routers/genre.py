from fastapi import status, Depends, APIRouter, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import schemas, oauth2, database
from ..database import get_db
from ..repository import genre


router = APIRouter(
    prefix="/genre",
    tags=["Genres"]
)


@router.get("/all", 
            response_model=List[schemas.GenreResponse])
async def get_genre_all(db: Session = Depends(database.get_db), 
                        limit: int = 5, 
                        skip: int = 0, 
                        search: Optional[str] = ''):
    
    return genre.get_genre_all(db, limit, skip, search)


@router.get("/{genre_id}", 
            response_model=schemas.GenreResponse)
async def get_genre_by_id(genre_id: int, 
                          db: Session = Depends(database.get_db)):

    return genre.get_genre_by_id(genre_id, db)


@router.post("/create", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.GenreResponse)
async def create_genre(new_genre: schemas.GenreCreate, 
                       db: Session = Depends(database.get_db), 
                       current_user = Depends(oauth2.get_current_user)):

    return genre.create_genre(new_genre, db, current_user)


@router.put("/update/{genre_id}", 
            response_model=schemas.GenreResponse, 
            status_code=status.HTTP_200_OK)
async def update_genre(genre_id: int, 
                           new_genre: schemas.GenreUpdate, 
                           db: Session = Depends(database.get_db), 
                           current_user = Depends(oauth2.get_current_user)):

    return genre.update_genre(genre_id, new_genre, db, current_user)


@router.delete("/delete/{genre_id}")
async def delete_genre(genre_id: int, 
                       db: Session = Depends(database.get_db), 
                       current_user = Depends(oauth2.get_current_user)):

    return genre.delete_genre(genre_id, db, current_user)





# @router.post("/upload/")
# async def upload_file(file: UploadFile = File(...), 
#                       db: Session = Depends(get_db), 
#                       current_user = Depends(oauth2.get_current_user)):

#     return genre.upload_file(file, db, current_user)


# @router.get("/download/")
# async def download_file(db: Session = Depends(get_db), 
#                       current_user = Depends(oauth2.get_current_user)):

#     return genre.download_file(db, current_user)


