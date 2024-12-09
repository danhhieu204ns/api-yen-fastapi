from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from author.models.author import Author
from author.schemas.author import AuthorResponse, AuthorCreate, AuthorUpdate, AuthorPageableResponse
import math


router = APIRouter(
    prefix="/author",
    tags=["Author"],
)


@router.get("/all",
            response_model=list[AuthorResponse],
            status_code=status.HTTP_200_OK)
async def get_authors(
        db: Session = Depends(get_db)
    ):

    try:
        authors = db.query(Author).all()

        return authors
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable",
            response_model=AuthorPageableResponse,
            status_code=status.HTTP_200_OK)
async def get_author_pageable(
        page: int,
        page_size: int,
        db: Session = Depends(get_db)
    ):

    try:
        total_count = db.query(Author).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        authors = db.query(Author).offset(offset).limit(page_size).all()

        authors_pageable_res = AuthorPageableResponse(
            authors=authors,
            total_pages=total_pages,
            total_data=total_count
        )

        return authors_pageable_res
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/{id}",
            response_model=AuthorResponse,
            status_code=status.HTTP_200_OK)
async def search_author_by_id(
        id: int,
        db: Session = Depends(get_db)
    ):

    try:
        author = db.query(Author).filter(Author.id == id).first()
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tác giả không tồn tại"
            )
        
        return author
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/search/by-name/{name}",
            response_model=list[AuthorResponse])
async def search_authors_by_name(
        name: str,
        db: Session = Depends(get_db)
    ):

    try:
        authors = db.query(Author).filter(Author.name.ilike(f"%{name}%")).all()
        if not authors:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tác giả không tồn tại"
            )

        return authors
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/create",
                response_model=AuthorResponse,
                status_code=status.HTTP_201_CREATED)
async def create_author(
        new_author: AuthorCreate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        author = db.query(Author).filter(Author.name == new_author.name).first()
        if author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tác giả đã tồn tại"
            )

        author = Author(**new_author.dict())
        db.add(author)
        db.commit()

        return author
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu"
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/import",
            response_model=list[AuthorResponse],
            status_code=status.HTTP_201_CREATED)
async def import_authors(
        authors: list[AuthorCreate],
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        authors = [Author(**author.dict()) for author in authors]
        db.add_all(authors)
        db.commit()

        return authors
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu"
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.put("/update/{id}",
            response_model=AuthorResponse,
            status_code=status.HTTP_200_OK)
async def update_author(
        id: int,
        new_author: AuthorUpdate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        author = db.query(Author).filter(Author.id == id)
        if not author.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tác giả không tồn tại"
            )
        
        author.update(new_author.dict(), 
                    synchronize_session=False)
        db.commit()

        return author.first()
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu"
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete/{id}",
                status_code=status.HTTP_200_OK)
async def delete_author(
        id: int,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        author = db.query(Author).filter(Author.id == id)
        if not author.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tác giả không tồn tại"
            )

        author.delete(synchronize_session=False)
        db.commit()

        return {"message": "Xóa tác giả thành công"}
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu"
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete-many",
                status_code=status.HTTP_200_OK)
async def delete_authors(
        ids: list[int],
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        authors = db.query(Author).filter(Author.id.in_(ids))
        if not authors.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tác giả không tồn tại"
            )

        authors.delete(synchronize_session=False)
        db.commit()

        return {"message": "Xóa danh sách tác giả thành công"}
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu"
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete-all",
                status_code=status.HTTP_200_OK)
async def delete_all_authors(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        db.query(Author).delete()
        db.commit()

        return {"message": "Xóa tất cả tác giả thành công"}
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu"
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
