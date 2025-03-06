from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.params import File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, aliased
from sqlalchemy.exc import SQLAlchemyError
from book.models.book import Book
from book_copy.models.book_copy import BookCopy
from configs.authentication import get_current_user
from configs.database import get_db
from borrow.models.borrow import Borrow
from borrow.schemas.borrow import *
from role.models.role import Role
from user.models.user import User
from user_role.models.user_role import UserRole
import math
import pandas as pd


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
        UserAlias = aliased(User, name="borrower")
        StaffAlias = aliased(User, name="staff")
        
        borrows_query = db.query(
            Borrow,
            BookCopy,
            Book,
            UserAlias,
            StaffAlias
        )\
            .join(BookCopy, Borrow.book_copy_id == BookCopy.id)\
            .join(Book, BookCopy.book_id == Book.id)\
            .join(UserAlias, Borrow.user_id == UserAlias.id)\
            .outerjoin(StaffAlias, Borrow.staff_id == StaffAlias.id)
        
        borrows_data = borrows_query.all()
        
        borrows = []
        for borrow, book_copy, book, user, staff in borrows_data:
            borrow_response = {
                "id": borrow.id,
                "borrow_date": borrow.borrow_date,
                "duration": borrow.duration,
                "created_at": borrow.created_at,
                "status": borrow.status,
                "book_copy_id": borrow.book_copy_id,
                "user_id": borrow.user_id,
                "staff_id": borrow.staff_id,
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "username": user.username,
                    "phone_number": user.phone_number
                },
                "book_copy": {
                    "id": book_copy.id,
                    "status": book_copy.status,
                    "book": {
                        "id": book.id,
                        "name": book.name
                    }
                },
                "staff": {
                    "id": staff.id,
                    "full_name": staff.full_name,
                    "username": staff.username,
                    "phone_number": staff.phone_number
                } if staff else None
            }
            borrows.append(borrow_response)

        return ListBorrowResponse(
            borrows=borrows,
            total_data=len(borrows)
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
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
        UserAlias = aliased(User, name="borrower")
        StaffAlias = aliased(User, name="staff")
        
        base_query = db.query(
            Borrow,
            BookCopy,
            Book,
            UserAlias,
            StaffAlias
        )\
            .join(BookCopy, Borrow.book_copy_id == BookCopy.id)\
            .join(Book, BookCopy.book_id == Book.id)\
            .join(UserAlias, Borrow.user_id == UserAlias.id)\
            .outerjoin(StaffAlias, Borrow.staff_id == StaffAlias.id)
        
        total_count = base_query.count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size

        borrows_data = base_query.offset(offset).limit(page_size).all()
        
        borrows = []
        for borrow, book_copy, book, user, staff in borrows_data:
            borrow_response = {
                "id": borrow.id,
                "borrow_date": borrow.borrow_date,
                "duration": borrow.duration,
                "created_at": borrow.created_at,
                "status": borrow.status,
                "book_copy_id": borrow.book_copy_id,
                "user_id": borrow.user_id,
                "staff_id": borrow.staff_id,
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "username": user.username,
                    "phone_number": user.phone_number
                },
                "book_copy": {
                    "id": book_copy.id,
                    "status": book_copy.status,
                    "book": {
                        "id": book.id,
                        "name": book.name
                    }
                },
                "staff": {
                    "id": staff.id,
                    "full_name": staff.full_name,
                    "username": staff.username,
                    "phone_number": staff.phone_number
                } if staff else None
            }
            borrows.append(borrow_response)

        return BorrowPageableResponse(
            total_data=total_count,
            total_pages=total_pages,
            borrows=borrows
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
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
        UserAlias = aliased(User, name="borrower")
        StaffAlias = aliased(User, name="staff")
        
        borrow_data = db.query(
            Borrow,
            BookCopy,
            Book,
            UserAlias,
            StaffAlias
        )\
            .join(BookCopy, Borrow.book_copy_id == BookCopy.id)\
            .join(Book, BookCopy.book_id == Book.id)\
            .join(UserAlias, Borrow.user_id == UserAlias.id)\
            .outerjoin(StaffAlias, Borrow.staff_id == StaffAlias.id)\
            .filter(Borrow.id == id).first()

        if not borrow_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phiếu mượn không tồn tại"
            )
        
        borrow, book_copy, book, user, staff = borrow_data
        
        borrow_response = {
            "id": borrow.id,
            "borrow_date": borrow.borrow_date,
            "duration": borrow.duration,
            "created_at": borrow.created_at,
            "status": borrow.status,
            "book_copy_id": borrow.book_copy_id,
            "user_id": borrow.user_id,
            "staff_id": borrow.staff_id,
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "username": user.username,
                "phone_number": user.phone_number
            },
            "book_copy": {
                "id": book_copy.id,
                "status": book_copy.status,
                "book": {
                    "id": book.id,
                    "name": book.name
                }
            },
            "staff": {
                "id": staff.id,
                "full_name": staff.full_name,
                "username": staff.username,
                "phone_number": staff.phone_number
            } if staff else None
        }
        
        return borrow_response
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.post("/search",
             response_model=BorrowPageableResponse,
             status_code=status.HTTP_200_OK)
async def search_borrows(
        search_borrow: BorrowSearch,
        page: int = 1,
        page_size: int = 10,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        UserAlias = aliased(User, name="borrower")
        StaffAlias = aliased(User, name="staff")
        
        base_query = db.query(
            Borrow,
            BookCopy,
            Book,
            UserAlias,
            StaffAlias
        )\
            .join(BookCopy, Borrow.book_copy_id == BookCopy.id)\
            .join(Book, BookCopy.book_id == Book.id)\
            .join(UserAlias, Borrow.user_id == UserAlias.id)\
            .outerjoin(StaffAlias, Borrow.staff_id == StaffAlias.id)
        
        if search_borrow.duration:
            base_query = base_query.filter(Borrow.duration == search_borrow.duration)
        if search_borrow.status:
            base_query = base_query.filter(Borrow.status == search_borrow.status)
        if search_borrow.book_copy_id:
            base_query = base_query.filter(Borrow.book_copy_id == search_borrow.book_copy_id)
        if search_borrow.user_id:
            base_query = base_query.filter(Borrow.user_id == search_borrow.user_id)
        if search_borrow.staff_id:
            base_query = base_query.filter(Borrow.staff_id == search_borrow.staff_id)

        total_count = base_query.count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size

        borrows_data = base_query.offset(offset).limit(page_size).all()
        
        borrows = []
        for borrow, book_copy, book, user, staff in borrows_data:
            borrow_response = {
                "id": borrow.id,
                "borrow_date": borrow.borrow_date,
                "duration": borrow.duration,
                "created_at": borrow.created_at,
                "status": borrow.status,
                "book_copy_id": borrow.book_copy_id,
                "user_id": borrow.user_id,
                "staff_id": borrow.staff_id,
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "username": user.username,
                    "phone_number": user.phone_number
                },
                "book_copy": {
                    "id": book_copy.id,
                    "status": book_copy.status,
                    "book": {
                        "id": book.id,
                        "name": book.name
                    }
                },
                "staff": {
                    "id": staff.id,
                    "full_name": staff.full_name,
                    "username": staff.username,
                    "phone_number": staff.phone_number
                } if staff else None
            }
            borrows.append(borrow_response)

        return BorrowPageableResponse(
            borrows=borrows,
            total_data=total_count,
            total_pages=total_pages
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/create")
async def create_borrow(
        new_borrow: BorrowCreate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:

        if not db.query(Book).filter(Book.id == new_borrow.book_id).first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sách không tồn tại"
            )
        
        book_copy = db.query(BookCopy)\
            .join(Book, BookCopy.book_id == Book.id)\
            .filter(Book.id == new_borrow.book_id, 
                    BookCopy.status == "Có sẵn")
        
        if not book_copy.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hiện không còn bản sao của sách này"
            )
        
        if new_borrow.user_id and not db.query(User).filter(User.id == new_borrow.user_id).first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Người mượn không tồn tại"
            )
        
        if new_borrow.staff_id and not db.query(User).filter(User.id == new_borrow.staff_id).first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nhân viên không tồn tại"
            )
        
        if new_borrow.duration and new_borrow.duration < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thời hạn không hợp lệ"
            )
        
        is_admin = db.query(User)\
            .join(UserRole)\
            .join(Role)\
            .filter(User.id == current_user.id, Role.name == "admin").first()

        borrow = Borrow(
            duration=new_borrow.duration,
            status="Đang mượn" if is_admin else "Đang chờ",
            book_copy_id=book_copy.first().id,
            user_id=new_borrow.user_id if new_borrow.user_id else current_user.id,
            staff_id=new_borrow.staff_id
        )
        db.add(borrow)
        db.flush()

        book_copy_to_update = db.query(BookCopy).filter(BookCopy.id == book_copy.first().id)
        book_copy_to_update.update({"status": "Đã mượn"})
        db.commit()

        return JSONResponse(
            content={"message": "Tạo phiếu mượn thành công"},
            status_code=status.HTTP_201_CREATED
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/import")
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
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.put("/update/{id}")
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
        
        if updated_borrow.status == "Đã trả":
            book_copy_to_update = db.query(BookCopy).filter(BookCopy.id == borrow.first().book_copy_id)
            book_copy_to_update.update({"status": "Có sẵn"})

        borrow.update(updated_borrow.dict(), synchronize_session=False)
        db.commit()

        return JSONResponse(
            content={"message": "Cập nhật phiếu mượn thành công"},
            status_code=status.HTTP_200_OK
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.delete("/delete/{id}")
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
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete-many")
async def delete_borrows(
        ids: DeleteMany,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        borrows = db.query(Borrow).filter(Borrow.id.in_(ids.ids))
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

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete-all")
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
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
