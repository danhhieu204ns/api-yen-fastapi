from io import BytesIO
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from author.models.author import Author
from category.models.category import Category
from publisher.models.publisher import Publisher
from configs.authentication import get_current_user
from configs.database import get_db
from book.models.book import Book
from book.schemas.book import *
import math
import pandas as pd


router = APIRouter(
    prefix="/book",
    tags=["Book"],
)


@router.get("/all",
            response_model=ListBookResponse,
            status_code=status.HTTP_200_OK)
async def get_books(
        db: Session = Depends(get_db)
    ):

    try:
        books = db.query(Book).all()

        return ListBookResponse(
            books=books, 
            total_data=len(books)
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable",
            response_model=BookPageableResponse,
            status_code=status.HTTP_200_OK)
async def get_genres_pageable(
        page: int,
        page_size: int,
        db: Session = Depends(get_db)
    ):

    try:
        total_data = db.query(Book).count()
        total_pages = math.ceil(total_data / page_size)
        offset = (page - 1) * page_size

        books = db.query(Book).offset(offset).limit(page_size).all()

        return BookPageableResponse(
            total_data=total_data,
            total_pages=total_pages,
            books=books
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
        

@router.get("/export",
            status_code=status.HTTP_200_OK)
async def export_books(
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        books = db.query(Book).all()
        df = pd.DataFrame([{
            "Số thứ tự": index + 1,
            "Tên sách": book.name,
            "Trạng thái": book.status,
            "Tóm tắt": book.summary,
            "Số trang": book.pages,
            "Ngôn ngữ": book.language,
            "Tác giả": book.author.name if book.author else "Không có tác giả",
            "Nhà xuất bản": book.publisher.name if book.publisher else "Không có NXB",
            "Thể loại": book.category.name if book.category else "Không có thể loại"
        } for index, book in enumerate(books)])

        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Books', index=False)
        writer.close()
        output.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="authors.xlsx"'
        }
        
        return StreamingResponse(
            output,
            headers=headers,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/{id}",
            response_model=BookResponse,
            status_code=status.HTTP_200_OK)
async def get_book_by_id(
        id: int,
        db: Session = Depends(get_db)
    ):

    try:
        book = db.query(Book).filter(Book.id == id).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sách không tồn tại"
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"book": book}
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/search",
            response_model=BookPageableResponse, 
            status_code=status.HTTP_200_OK)
async def search_books(
        info: BookSearch,
        page: int,
        page_size: int,
        db: Session = Depends(get_db)
    ):

    try:
        books = db.query(Book)
        if info.name:
            books = books.filter(Book.name.like(f"%{info.name.strip().lower()}%"))

        total_data = books.count()
        total_pages = math.ceil(total_data / page_size)
        offset = (page - 1) * page_size

        books = books.offset(offset).limit(page_size).all()    
        
        return BookPageableResponse(
            books=books, 
            total_data=len(books), 
            total_pages=total_pages
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/create",
            status_code=status.HTTP_201_CREATED)
async def create_book(
        new_book: BookCreate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        book = db.query(Book).filter(Book.name == new_book.name).first()
        if book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sách đã tồn tại"
            )

        book = Book(**new_book.dict())
        db.add(book)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Thêm sách thành công"}
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
            response_model=ListBookResponse,
            status_code=status.HTTP_201_CREATED)
async def import_books(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    COLUMN_MAPPING = {
        "Tên sách": "name",
        "Trạng thái": "status",
        "Tóm tắt": "summary",
        "Số trang": "pages",
        "Ngôn ngữ": "language",
        "Tác giả": "author_name",
        "Nhà xuất bản": "publisher_name",
        "Thể loại": "category_name"
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
    
    author_map = {a.name: a.id for a in db.query(Author).all()}
    publisher_map = {p.name: p.id for p in db.query(Publisher).all()}
    category_map = {c.name: c.id for c in db.query(Category).all()}
    
    errors = []
    list_books = []
    
    for index, row in df.iterrows():
        name = row.get("name")
        if not name:
            errors.append({"Dòng": index + 2, "Lỗi": "Tên sách không được để trống."})
            continue
        
        author_id = author_map.get(row.get("author_name"))
        publisher_id = publisher_map.get(row.get("publisher_name"))
        category_id = category_map.get(row.get("category_name"))
        
        status = None if pd.isna(row.get("status")) else row.get("status")
        summary = None if pd.isna(row.get("summary")) else row.get("summary")
        pages = None if pd.isna(row.get("pages")) else int(row.get("pages"))
        language = None if pd.isna(row.get("language")) else row.get("language")
        
        book = Book(
            name=name,
            status=status,
            summary=summary,
            pages=pages,
            language=language,
            author_id=author_id,
            publisher_id=publisher_id,
            category_id=category_id
        )
        list_books.append(book)
    
    if errors:
        return JSONResponse(
            status_code=400, 
            content={"errors": errors}
        )
    
    try:
        db.bulk_save_objects(list_books)
        db.commit()
        return JSONResponse(
            status_code=201, 
            content={"message": "Import sách thành công"}
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
async def update_book(
        id: int,
        book: BookUpdate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        book_db = db.query(Book).filter(Book.id == id)
        if not book_db.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sách không tồn tại"
            )

        book_db.update(book.dict(), synchronize_session=False)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Cập nhật sách thành công"}
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
async def delete_book(
        id: int,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        book = db.query(Book).filter(Book.id == id)
        if not book.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sách không tồn tại"
            )

        book.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa sách thành công"}
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
async def delete_books(
        ids: DeleteMany,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        books = db.query(Book).filter(Book.id.in_(ids.ids))
        if not books.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sách không tồn tại"
            )

        books.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa sách thành công"}
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
async def delete_all_books(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        db.query(Book).delete()
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa tất cả sách thành công"}
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
    