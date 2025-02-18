from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from category.models.category import Category
from category.schemas.category import *
import math
import pandas as pd


router = APIRouter(
    prefix="/category",
    tags=["Category"],
)


@router.get("/all",
            response_model=ListCategoryResponse,
            status_code=status.HTTP_200_OK)
async def get_categories(
        db: Session = Depends(get_db)
    ):

    try:
        categories = db.query(Category).all()
        
        return ListCategoryResponse(
            categories=categories,
            total_data=len(categories)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable",
            response_model=CategoryPageableResponse,
            status_code=status.HTTP_200_OK)
async def get_categories_pageable(
        page: int,
        page_size: int,
        db: Session = Depends(get_db)
    ):

    try:
        total_count = db.query(Category).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        categories = db.query(Category).offset(offset).limit(page_size).all()

        return CategoryPageableResponse(
            categories=categories,
            total_pages=total_pages,
            total_data=total_count
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/export", status_code=status.HTTP_200_OK)
async def export_categories(db: Session = Depends(get_db)):
    try:
        categories = db.query(Category).all()
        df = pd.DataFrame([{
            "id": c.id,
            "name": c.name,
            "age_limit": c.age_limit,
            "description": c.description
        } for c in categories])

        # Kiểm tra nếu không có dữ liệu
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không có dữ liệu để xuất"
            )

        # Tạo file Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Categories")
        output.seek(0)

        headers = {
            "Content-Disposition": "attachment; filename=categories.xlsx",
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

        return StreamingResponse(output, headers=headers, media_type=headers["Content-Type"])

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/{id}",
            response_model=CategoryResponse,
            status_code=status.HTTP_200_OK)
async def search_category_by_id(
        id: int,
        db: Session = Depends(get_db)
    ):

    try:
        category = db.query(Category).filter(Category.id == id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thể loại không tồn tại"
            )

        return category
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/search",
            response_model=CategoryPageableResponse,
            status_code=status.HTTP_200_OK)
async def search_category(
        info: CategorySearch,
        page: int,
        page_size: int,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        category = db.query(Category)
        if info.name:
            category = category.filter(Category.name.like(f"%{info.name}%"))
        if info.age_limit:
            category = category.filter(Category.age_limit == info.age_limit)
        if info.description:
            category = category.filter(Category.description.like(f"%{info.description}%"))

        total_count = category.count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        categories = category.offset(offset).limit(page_size).all()

        return CategoryPageableResponse(
            categories=categories,
            total_pages=total_pages,
            total_data=total_count
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/create",
            response_model=CategoryResponse,
            status_code=status.HTTP_201_CREATED)
async def create_category(
        new_category: CategoryCreate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        category = db.query(Category).filter(Category.name == new_category.name).first()
        if category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thể loại đã tồn tại"
            )

        category = Category(**new_category.dict())
        db.add(category)
        db.commit()

        return JSONResponse(
            content={"message": "Tạo thể loại thành công"},
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
async def import_categories(
        file: UploadFile,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    COLUMN_MAPPING = {
        "Tên danh mục": "name",
        "Giới hạn tuổi": "age_limit",
        "Mô tả": "description"
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
    
    existing_category_names = {c.name for c in db.query(Category).all()}
    errors = []
    list_categories = []
    
    for index, row in df.iterrows():
        name = row.get("name")
        if not name:
            errors.append({"Dòng": index + 2, "Lỗi": "Tên danh mục không được để trống."})
            continue
        
        if name in existing_category_names:
            errors.append({"Dòng": index + 2, "Lỗi": f"Danh mục '{name}' đã tồn tại."})
            continue
        
        age_limit = None if pd.isna(row.get("age_limit")) else int(row.get("age_limit"))
        description = None if pd.isna(row.get("description")) else row.get("description")
        
        category = Category(
            name=name,
            age_limit=age_limit,
            description=description
        )
        list_categories.append(category)
    
    if errors:
        return JSONResponse(
            content={"errors": errors},
            status_code=400
        )
    
    try:
        db.bulk_save_objects(list_categories)
        db.commit()
        return JSONResponse(
            content={"message": "Import danh sách thể loại thành công"},
            status_code=201
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.put("/update/{id}",
            response_model=CategoryResponse,
            status_code=status.HTTP_200_OK)
async def update_category(
        id: int,
        category: CategoryUpdate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        category_db = db.query(Category).filter(Category.id == id)
        if not category_db.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thể loại không tồn tại"
            )

        category_db.update(
            category.dict(), 
            synchronize_session=False
        )
        db.commit()

        return JSONResponse(
            content={"message": "Cập nhật thể loại thành công"},
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
async def delete_category(
        id: int,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        category = db.query(Category).filter(Category.id == id)
        if not category.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thể loại không tồn tại"
            )

        category.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            content={"message": "Xóa thể loại thành công"},
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
async def delete_categories(
        ids: CategoryDelete,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        categories = db.query(Category).filter(Category.id.in_(ids.list_id))
        if not categories.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thể loại không tồn tại"
            )

        categories.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            content={"message": "Xóa danh sách thể loại thành công"},
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
async def delete_all_categories(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        db.query(Category).delete()
        db.commit()

        return JSONResponse(
            content={"message": "Xóa tất cả thể loại thành công"},
            status_code=status.HTTP_200_OK
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
