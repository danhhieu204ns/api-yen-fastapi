from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from borrow.models.borrow import Borrow
from borrow.schemas.borrow import BorrowCreate, BorrowResponse, BorrowUpdate, BorrowPageableResponse
import math


router = APIRouter(
    prefix="/borrow",
    tags=["Borrow"],
)


@router.get("/all",
            response_model=list[BorrowResponse],
            status_code=status.HTTP_200_OK)
async def get_borrows(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        borrows = db.query(Borrow).all()

        return borrows

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

        borrows_pageable = BorrowPageableResponse(
            total_count=total_count,
            total_pages=total_pages,
            borrows=borrows
        )

        return borrows_pageable
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/{id}",
            response_model=BorrowResponse,
            status_code=status.HTTP_200_OK)
async def search_borrow_by_id(
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


@router.post("/create",
            response_model=BorrowResponse,
            status_code=status.HTTP_201_CREATED)
async def create_borrow(
        new_borrow: BorrowCreate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        borrow = Borrow(**new_borrow.dict())
        db.add(borrow)
        db.commit()

        return borrow
    
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
            response_model=list[BorrowResponse],
            status_code=status.HTTP_201_CREATED)
async def import_borrows(
        new_borrows: list[BorrowCreate],
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        borrows = [Borrow(**borrow.dict()) for borrow in new_borrows]
        db.add_all(borrows)
        db.commit()

        return borrows
    
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
            response_model=BorrowResponse,
            status_code=status.HTTP_200_OK)
async def update_borrow(
        id: int,
        new_borrow: BorrowUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
    ):

    try:
        borrow_query = db.query(Borrow).filter(Borrow.id == id)
        borrow = borrow_query.first()

        if not borrow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phiếu mượn không tồn tại"
            )
        
        borrow_query.update(new_borrow.dict(), synchronize_session=False)
        db.commit()
        
        return borrow_query.first()
    
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

        return {"message": "Xóa phiếu mượn thành công"}
    
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

        return {"message": "Xóa danh sách phiếu mượn thành công"}
    
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

        return {"message": "Xóa tất cả phiếu mượn thành công"}
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
