from io import BytesIO
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from bookshelf.models.bookshelf import Bookshelf
from bookshelf.schemas.bookshelf import *
import math
import pandas as pd


router = APIRouter(
    prefix="/bookshelf",
    tags=["Bookshelf"],
)


@router.get("/all",
            response_model=ListBookshelfResponse,
            status_code=status.HTTP_200_OK)
async def get_bookshelfs(
        db: Session = Depends(get_db)
    ):

    try:
        bookshelfs = db.query(Bookshelf).all()

        return ListBookshelfResponse(
            bookshelfs=bookshelfs,
            total_data=len(bookshelfs)
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable",
            response_model=BookshelfPageableResponse,
            status_code=status.HTTP_200_OK)
async def get_bookshelf_pageable(
        page: int,
        page_size: int,
        db: Session = Depends(get_db)
    ):

    try:
        total_count = db.query(Bookshelf).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size

        bookshelfs = db.query(Bookshelf).offset(offset).limit(page_size).all()

        return BookshelfPageableResponse(
            total_data=total_count,
            total_pages=total_pages,
            bookshelfs=bookshelfs
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/{id}",
            response_model=BookshelfResponse,
            status_code=status.HTTP_200_OK)
async def get_bookshelf_by_id(
        id: int,
        db: Session = Depends(get_db)
    ):

    try:
        bookshelf = db.query(Bookshelf).filter(Bookshelf.id == id).first()
        if not bookshelf:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tủ sách không tồn tại"
            )
        
        return bookshelf
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/search",
            response_model=ListBookshelfResponse, 
            status_code=status.HTTP_200_OK)
async def search_bookshelf(
        info: BookshelfSearch,
        db: Session = Depends(get_db)
    ):

    try:
        bookshelfs = db.query(Bookshelf)
        if info.name:
            bookshelfs = bookshelfs.filter(Bookshelf.name.like(f"%{info.name}%"))
        if info.status:
            bookshelfs = bookshelfs.filter(Bookshelf.status == info.status)
        
        bookshelfs = bookshelfs.all()
        
        return ListBookshelfResponse(
            bookshelfs=bookshelfs,
            total_data=len(bookshelfs)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/create",
            response_model=BookshelfResponse,
            status_code=status.HTTP_201_CREATED)
async def create_bookshelf(
        new_bookshelf: BookshelfCreate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        bookshelf = db.query(Bookshelf).filter(Bookshelf.name == new_bookshelf.name).first()
        if bookshelf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tủ sách đã tồn tại"
            )

        bookshelf = Bookshelf(**new_bookshelf.dict())
        db.add(bookshelf)
        db.commit()

        return JSONResponse(
            content={"message": "Tạo tủ sách thành công"},
            status_code=status.HTTP_201_CREATED
        )
    
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
            response_model=list[BookshelfResponse],
            status_code=status.HTTP_201_CREATED)
async def import_bookshelfs(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    COLUMN_MAPPING = {
        "Tên kệ sách": "name",
        "Trạng thái": "status"
    }
    
    if file.content_type not in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
        raise HTTPException(
            status_code=400, 
            detail="File không hợp lệ. Vui lòng upload file Excel."
        )
    
    content = await file.read()

    try:
        df = pd.read_excel(BytesIO(content))
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Lỗi đọc file: {str(e)}"
        )
    
    try:
        df.rename(columns=COLUMN_MAPPING, inplace=True)
    except KeyError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Tiêu đề cột không hợp lệ: {str(e)}"
        )
    
    errors = []
    list_bookshelves = []
    
    for index, row in df.iterrows():
        name = row.get("name")
        if not name:
            errors.append({"Dòng": index + 2, "Lỗi": "Tên kệ sách không được để trống."})
            continue
        
        if db.query(Bookshelf).filter_by(name=name).first():
            errors.append({"Dòng": index + 2, "Lỗi": f"Kệ sách '{name}' đã tồn tại."})
            continue
        
        status = None if pd.isna(row.get("status")) else row.get("status")
        
        bookshelf = Bookshelf(
            name=name,
            status=status
        )
        list_bookshelves.append(bookshelf)
    
    if errors:
        return JSONResponse(
            content={"errors": errors},
            status_code=400
        )
    
    try:
        db.bulk_save_objects(list_bookshelves)
        db.commit()
        return JSONResponse(
            content={"message": "Import dữ liệu thành công"},
            status_code=201
        )
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, 
            detail="Lỗi khi lưu dữ liệu vào database."
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu"
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.put("/update/{id}",
            response_model=BookshelfResponse,
            status_code=status.HTTP_200_OK)
async def update_bookshelf(
        id: int,
        bookshelf: BookshelfUpdate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        bookshelf_db = db.query(Bookshelf).filter(Bookshelf.id == id)
        if not bookshelf_db.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tủ sách không tồn tại"
            )

        bookshelf_db.update(
            bookshelf.dict(), 
            synchronize_session=False
        )
        db.commit()

        return JSONResponse(
            content={"message": "Cập nhật tủ sách thành công"},
            status_code=status.HTTP_200_OK
        )
    
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
async def delete_bookshelf(
        id: int,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        bookshelf = db.query(Bookshelf).filter(Bookshelf.id == id)
        if not bookshelf.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tủ sách không tồn tại"
            )

        bookshelf.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            content={"message": "Xóa tủ sách thành công"},
            status_code=status.HTTP_200_OK
        )
    
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
async def delete_bookshelfs(
        ids: DeleteMany,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        bookshelfs = db.query(Bookshelf).filter(Bookshelf.id.in_(ids.ids))
        if not bookshelfs.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tủ sách không tồn tại"
            )

        bookshelfs.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            content={"message": "Xóa danh sách tủ sách thành công"},
            status_code=status.HTTP_200_OK
        )
    
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
async def delete_all_bookshelfs(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        db.query(Bookshelf).delete()
        db.commit()

        return JSONResponse(
            content={"message": "Xóa tất cả tủ sách thành công"},
            status_code=status.HTTP_200_OK
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
