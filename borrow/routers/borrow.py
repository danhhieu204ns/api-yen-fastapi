from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.params import File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from book.models.book import Book
from book_copy.models.book_copy import BookCopy
from configs.authentication import get_current_user
from configs.database import get_db
from borrow.models.borrow import Borrow
from borrow.schemas.borrow import *
import math
import pandas as pd

from user.models.user import User


router = APIRouter(
    prefix="/borrow",
    tags=["Borrow"],
)


@router.get("/all",
            response_model=ListBorrowResponse,
            status_code=status.HTTP_200_OK)
async def get_borrows(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        borrows = db.query(Borrow).all()

        return ListBorrowResponse(
            borrows=borrows,
            total_data=len(borrows)
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable",
            response_model=BorrowPageableResponse,
            status_code=status.HTTP_200_OK)
async def get_borrows_pageable(
        page: int = 1,
        page_size: int = 10,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        total_count = db.query(Borrow).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size

        borrows = db.query(Borrow).offset(offset).limit(page_size).all()

        return BorrowPageableResponse(
            total_data=total_count,
            total_pages=total_pages,
            borrows=borrows
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/{id}",
            response_model=BorrowResponse,
            status_code=status.HTTP_200_OK)
async def get_borrow_by_id(
        id: int,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        borrow = db.query(Borrow).filter(Borrow.id == id).first()

        if not borrow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phiếu mượn không tồn tại"
            )
        
        return borrow
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.post("/search",
             response_model=ListBorrowResponse,
             status_code=status.HTTP_200_OK)
async def search_borrows(
        search_borrow: BorrowSearch,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        borrows = db.query(Borrow)
        if search_borrow.duration:
            borrows = borrows.filter(Borrow.duration == search_borrow.duration)
        if search_borrow.status:
            borrows = borrows.filter(Borrow.status == search_borrow.status)
        if search_borrow.book_copy_id:
            borrows = borrows.filter(Borrow.book_copy_id == search_borrow.book_copy_id)
        if search_borrow.user_id:
            borrows = borrows.filter(Borrow.user_id == search_borrow.user_id)
        if search_borrow.staff_id:
            borrows = borrows.filter(Borrow.staff_id == search_borrow.staff_id)

        borrows = borrows.all()

        return ListBorrowResponse(
            borrows=borrows,
            total_data=len(borrows)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/create",
            response_model=BorrowResponse,
            status_code=status.HTTP_201_CREATED)
async def create_borrow(
        new_borrow: BorrowCreate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:

        if not db.query(BookCopy).filter(BookCopy.id == new_borrow.book_copy_id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bản sao sách không tồn tại"
            )
        
        if not db.query(User).filter(User.id == new_borrow.user_id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người mượn không tồn tại"
            )
        
        if new_borrow.staff_id and not db.query(User).filter(User.id == new_borrow.staff_id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nhân viên không tồn tại"
            )
        
        if new_borrow.status and new_borrow.status not in ["PENDING", "APPROVED", "REJECTED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trạng thái không hợp lệ"
            )
        
        if new_borrow.duration and new_borrow.duration < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thời hạn không hợp lệ"
            )

        borrow = Borrow(**new_borrow.dict())
        db.add(borrow)
        db.commit()

        return JSONResponse(
            content={"message": "Tạo phiếu mượn thành công"},
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
            status_code=status.HTTP_201_CREATED)
async def import_borrows(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    COLUMN_MAPPING = {
        "Thời hạn": "duration",
        "Trạng thái": "status",
        "Tên sách": "book_name",
        "Người mượn": "user_name",
        "Nhân viên": "staff_name"
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
    book_copy_to_id = {bc.book_id: bc.id for bc in db.query(BookCopy).all()}
    user_name_to_id = {u.name: u.id for u in db.query(User).all()}
    staff_name_to_id = {s.name: s.id for s in db.query(User).all()}
    
    errors = []
    list_borrows = []
    
    for index, row in df.iterrows():
        book_id = book_name_to_id.get(row.get("book_name"))
        book_copy_id = book_copy_to_id.get(book_id) if book_id else None
        user_id = user_name_to_id.get(row.get("user_name"))
        staff_id = staff_name_to_id.get(row.get("staff_name")) if row.get("staff_name") else None
        duration = row.get("duration")
        status = row.get("status", "PENDING")
        
        if not book_id:
            errors.append({"Dòng": index + 2, "Lỗi": f"Tên sách '{row.get('book_name')}' không tồn tại."})
            continue
        
        if not book_copy_id:
            errors.append({"Dòng": index + 2, "Lỗi": f"Không tìm thấy bản sao của sách '{row.get('book_name')}'"})
            continue
        
        if not user_id:
            errors.append({"Dòng": index + 2, "Lỗi": f"Người mượn '{row.get('user_name')}' không tồn tại."})
            continue
        
        borrow = Borrow(
            duration=duration,
            status=status,
            book_copy_id=book_copy_id,
            user_id=user_id,
            staff_id=staff_id
        )
        list_borrows.append(borrow)
    
    if errors:
        return JSONResponse(
            content={"errors": errors},
            status_code=400
        )
    
    try:
        db.bulk_save_objects(list_borrows)
        db.commit()
        return JSONResponse(
            content={"message": "Import phiếu mượn thành công"},
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
            status_code=500,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.put("/update/{id}", 
            status_code=status.HTTP_200_OK)
async def update_borrow(
        id: int,
        updated_borrow: BorrowUpdate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        borrow = db.query(Borrow).filter(Borrow.id == id)
        if not borrow.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phiếu mượn không tồn tại"
            )
        
        update_data = updated_borrow.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(borrow, key, value)
        db.commit()

        return JSONResponse(
            content={"message": "Cập nhật phiếu mượn thành công"},
            status_code=status.HTTP_200_OK
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu"
        )


@router.delete("/delete/{id}",
            status_code=status.HTTP_200_OK)
async def delete_borrow(
        id: int,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        borrow = db.query(Borrow).filter(Borrow.id == id)
        if not borrow.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phiếu mượn không tồn tại"
            )
        
        borrow.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            content={"message": "Xóa phiếu mượn thành công"},
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
async def delete_borrows(
        ids: list[int],
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        borrows = db.query(Borrow).filter(Borrow.id.in_(ids))
        if not borrows.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phiếu mượn không tồn tại"
            )
        
        borrows.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            content={"message": "Xóa danh sách phiếu mượn thành công"},
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
async def delete_all_borrows(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        db.query(Borrow).delete()
        db.commit()

        return JSONResponse(
            content={"message": "Xóa tất cả phiếu mượn thành công"},
            status_code=status.HTTP_200_OK
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi không xác định: {str(e)}"
        )
