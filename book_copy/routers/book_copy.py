from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.params import File
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from book.models.book import Book
from bookshelf.models.bookshelf import Bookshelf
from configs.authentication import get_current_user
from configs.database import get_db
from book_copy.models.book_copy import BookCopy
from book_copy.schemas.book_copy import *
import math
import pandas as pd


router = APIRouter(
    prefix="/book-copy",
    tags=["Book_Copies"],
)


@router.get("/all",
            response_model=ListBookCopyResponse,
            status_code=status.HTTP_200_OK)
async def get_book_copies(
        db: Session = Depends(get_db)
    ):

    try:
        book_copies = db.query(BookCopy)\
            .join(Book)\
            .outerjoin(Bookshelf)\
            .options(
                joinedload(BookCopy.book),
                joinedload(BookCopy.bookshelf)
            )\
            .all()

        return ListBookCopyResponse(
            book_copies=book_copies, 
            total_data=len(book_copies)
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable",
            response_model=BookCopyPageableResponse,
            status_code=status.HTTP_200_OK)
async def get_book_copy_pageable(
        page: int,
        page_size: int,
        db: Session = Depends(get_db)
    ):

    try:
        total_count = db.query(BookCopy).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size

        book_copies = db.query(BookCopy)\
            .join(Book)\
            .outerjoin(Bookshelf)\
            .options(
                joinedload(BookCopy.book),
                joinedload(BookCopy.bookshelf)
            )\
            .offset(offset)\
            .limit(page_size)\
            .all()
            
        list_book_copies = [BookCopyResponse(
            id=book_copy.id,
            book=BookBase(**book_copy.book.__dict__),
            bookshelf=BookshelfBase(**book_copy.bookshelf.__dict__) if book_copy.bookshelf else None, 
            status=book_copy.status 
        ) for book_copy in book_copies]

        return BookCopyPageableResponse(
            total_data=total_count,
            total_pages=total_pages,
            book_copies=list_book_copies
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/export",
            status_code=status.HTTP_200_OK)
async def export_book_copies(
        db: Session = Depends(get_db)
    ):

    try:
        book_copies = db.query(BookCopy)\
            .join(Book)\
            .outerjoin(Bookshelf)\
            .options(
                joinedload(BookCopy.book),
                joinedload(BookCopy.bookshelf)
            )\
            .all()

        df = pd.DataFrame([{
            "Số thứ tự": index + 1,
            "Tên sách": book_copy.book.name,
            "Tên kệ sách": book_copy.bookshelf.name if book_copy.bookshelf else None,
            "Trạng thái": book_copy.status
        } for index, book_copy in enumerate(book_copies)])

        output = BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")
        df.to_excel(writer, sheet_name="Book_copy", index=False)
        writer.close()
        output.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="book_copies.xlsx"',
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }

        return StreamingResponse(output, headers=headers)

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/{id}",
            response_model=BookCopyResponse,
            status_code=status.HTTP_200_OK)
async def get_book_copy_by_id(
        id: int,
        db: Session = Depends(get_db)
    ):

    try:
        book_copy = db.query(BookCopy).filter(BookCopy.id == id).first()
        if not book_copy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bản sao sách không tồn tại"
            )
        
        return book_copy
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.post("/search",
            response_model=ListBookCopyResponse,
            status_code=status.HTTP_200_OK)
async def search_book_copy(
        search: BookCopySearch,
        page: int = 1,
        page_size: int = 10,
        db: Session = Depends(get_db)
    ):

    try:
        book_copies = db.query(BookCopy)

        if search.status:
            book_copies = book_copies.filter(BookCopy.status == search.status)

        total_count = book_copies.count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size

        book_copies = book_copies.offset(offset).limit(page_size).all()

        return ListBookCopyResponse(
            book_copies=book_copies, 
            total_data=total_count,
            total_pages=total_pages
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/create", 
            status_code=status.HTTP_201_CREATED)
async def create_book_copy(
        new_book_copy: BookCopyCreate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        book_copy = BookCopy(**new_book_copy.dict())
        db.add(book_copy)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Tạo bản sao sách thành công"}
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


@router.post("/import")
async def import_book_copies(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    COLUMN_MAPPING = {
        "Trạng thái": "status",
        "Tên sách": "book_name",
        "Tên kệ sách": "bookshelf_name"
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
    
    book_name_to_id = {b.name: b.id for b in db.query(Book).all()}
    bookshelf_name_to_id = {bs.name: bs.id for bs in db.query(Bookshelf).all()}
    
    errors = []
    list_book_copies = []
    
    for index, row in df.iterrows():
        book_id = book_name_to_id.get(row.get("book_name"))
        bookshelf_id = bookshelf_name_to_id.get(row.get("bookshelf_name")) if row.get("bookshelf_name") else None
        status = row.get("status", "AVAILABLE")
        
        if not book_id:
            errors.append({"Line": index + 2, "Error": f"Sách '{row.get('book_name')}' không tồn tại."})
            continue
        
        book_copy = BookCopy(
            status=status,
            book_id=book_id,
            bookshelf_id=bookshelf_id
        )
        list_book_copies.append(book_copy)
       
    if errors:
        return JSONResponse(
            status_code=400,
            content={"errors": errors}
        )
    
    try:
        db.bulk_save_objects(list_book_copies)
        db.commit()
        return JSONResponse(
            status_code=201,
            content={"message": "Nhập dữ liệu thành công"}
        )
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, 
            detail="Lỗi khi lưu dữ liệu vào database."
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.put("/update/{id}",
            status_code=status.HTTP_200_OK)
async def update_book_copy(
        id: int,
        book_copy: BookCopyUpdate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        book_copy_db = db.query(BookCopy).filter(BookCopy.id == id)
        if not book_copy_db.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bản sao sách không tồn tại"
            )

        book_copy_db.update(
            book_copy.dict(), 
            synchronize_session=False
        )
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Cập nhật bản sao sách thành công"}
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
async def delete_book_copy(
        id: int,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        book_copy = db.query(BookCopy).filter(BookCopy.id == id)
        if not book_copy.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bản sao sách không tồn tại"
            )

        book_copy.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa bản sao sách thành công"}
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
async def delete_book_copies(
        ids: DeleteMany, 
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        book_copies = db.query(BookCopy).filter(BookCopy.id.in_(ids.ids))
        if not book_copies.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bản sao sách không tồn tại"
            )

        book_copies.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa bản sao sách thành công"}
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
async def delete_all_book_copies(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        db.query(BookCopy).delete()
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa tất cả bản sao sách thành công"}
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
