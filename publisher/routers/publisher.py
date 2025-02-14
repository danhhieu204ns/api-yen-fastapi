from io import BytesIO
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from publisher.models.publisher import Publisher
from publisher.schemas.publisher import *
import math
import pandas as pd


router = APIRouter(
    prefix="/publisher",
    tags=["Publisher"],
)


@router.get("/all",
            response_model=ListPublisherResponse,
            status_code=status.HTTP_200_OK)
async def get_publishers(
        db: Session = Depends(get_db)
    ):

    try:
        publishers = db.query(Publisher).all()

        return ListPublisherResponse(
            publishers=publishers,
            total_data=len(publishers)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable",
            response_model=PublisherPageableResponse,
            status_code=status.HTTP_200_OK)
async def get_publishers_pageable(
        page: int,
        page_size: int,
        db: Session = Depends(get_db)
    ):

    try:
        total_count = db.query(Publisher).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        publishers = db.query(Publisher).offset(offset).limit(page_size).all()

        return PublisherPageableResponse(
            publishers=publishers,
            total_pages=total_pages,
            total_data=total_count
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/{id}",
            response_model=PublisherResponse,
            status_code=status.HTTP_200_OK)
async def search_publisher_by_id(
        id: int,
        db: Session = Depends(get_db)
    ):

    try:
        publisher = db.query(Publisher).filter(Publisher.id == id).first()
        if not publisher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nhà xuất bản không tồn tại"
            )

        return publisher
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/search",
            response_model=ListPublisherResponse, 
            status_code=status.HTTP_200_OK)
async def search_publisher(
        info: PublisherSearch,
        db: Session = Depends(get_db)
    ):

    try:
        publishers = db.query(Publisher)
        if info.name:
            publishers = publishers.filter(Publisher.name.like(f"%{info.name}%"))
        if info.phone_number:
            publishers = publishers.filter(Publisher.phone_number.like(f"%{info.phone_number}%"))
        if info.address:
            publishers = publishers.filter(Publisher.address.like(f"%{info.address}%"))

        publishers = publishers.all()

        return ListPublisherResponse(
            publishers=publishers,
            total_data=len(publishers)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/create",
            response_model=PublisherResponse,
            status_code=status.HTTP_201_CREATED)
async def create_publisher(
        new_publisher: PublisherCreate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        publisher = db.query(Publisher).filter(Publisher.name == new_publisher.name).first()
        if publisher:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nhà xuất bản đã tồn tại"
            )

        publisher = Publisher(**new_publisher.dict())
        db.add(publisher)
        db.commit()

        return publisher
    
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
async def import_publishers(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    COLUMN_MAPPING = {
        "Tên nhà xuất bản": "name",
        "Email": "email",
        "Địa chỉ": "address",
        "Số điện thoại": "phone_number"
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
    
    existing_publisher_names = {p.name for p in db.query(Publisher).all()}
    errors = []
    list_publishers = []
    
    for index, row in df.iterrows():
        name = row.get("name")
        if not name:
            errors.append({"Dòng": index + 2, "Lỗi": "Tên nhà xuất bản không được để trống."})
            continue
        
        if name in existing_publisher_names:
            errors.append({"Dòng": index + 2, "Lỗi": f"Nhà xuất bản '{name}' đã tồn tại."})
            continue
        
        email = None if pd.isna(row.get("email")) else row.get("email")
        address = None if pd.isna(row.get("address")) else row.get("address")
        phone_number = None if pd.isna(row.get("phone_number")) else str(row.get("phone_number"))
        
        publisher = Publisher(
            name=name,
            email=email,
            address=address,
            phone_number=phone_number
        )
        list_publishers.append(publisher)
    
    if errors:
        return JSONResponse(
            content={"errors": errors}, 
            status_code=400
        )
    
    try:

        db.bulk_save_objects(list_publishers)
        db.commit()
        return JSONResponse(
            content={"message": "Import nhà xuất bản thành công."}, 
            status_code=201
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


@router.put("/update/{id}",
            response_model=PublisherResponse,
            status_code=status.HTTP_200_OK)
async def update_publisher(
        id: int,
        new_publisher: PublisherUpdate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        publisher = db.query(Publisher).filter(Publisher.id == id)
        if not publisher.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nhà xuất bản không tồn tại"
            )

        publisher.update(new_publisher.dict(), synchronize_session=False)
        db.commit()

        return JSONResponse(
            content={"message": "Cập nhật nhà xuất bản thành công."},
            status_code=200
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
async def delete_publisher(
        id: int,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        publisher = db.query(Publisher).filter(Publisher.id == id)
        if not publisher.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nhà xuất bản không tồn tại"
            )

        publisher.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            content={"message": "Xóa nhà xuất bản thành công."},
            status_code=200
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
async def delete_publishers(
        publishers: DeleteMany,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        publishers = db.query(Publisher).filter(Publisher.id.in_(publishers.list_id))
        if not publishers.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nhà xuất bản không tồn tại"
            )

        publishers.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            content={"message": "Xóa danh sách nhà xuất bản thành công."},
            status_code=200
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
async def delete_all_publishers(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        db.query(Publisher).delete()
        db.commit()

        return JSONResponse(
            content={"message": "Xóa tất cả nhà xuất bản thành công."},
            status_code=200
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    