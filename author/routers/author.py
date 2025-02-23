from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import func
from configs.authentication import get_current_user
from configs.database import get_db
from author.models.author import Author
from author.schemas.author import *
import math
import pandas as pd
from io import BytesIO


router = APIRouter(
    prefix="/author",
    tags=["Author"],
)


@router.get("/all",
            response_model=ListAuthorResponse,
            status_code=status.HTTP_200_OK)
async def get_authors(
        db: Session = Depends(get_db)
    ):

    try:
        authors = db.query(Author).all()

        return ListAuthorResponse(
            authors=authors,
            total_data=len(authors)
        )
    
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
    

@router.get("/export", 
            status_code=status.HTTP_200_OK)
async def export_authors(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        authors = db.query(Author).all()
        df = pd.DataFrame([{
            "Số thứ tự": i + 1,
            "Tên tác giả": a.name,
            "Ngày sinh": a.birthdate,
            "Địa chỉ": a.address,
            "Bút danh": a.pen_name,
            "Tiểu sử": a.biography
        } for i, a in enumerate(authors)])
        
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Authors', index=False)
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
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Lỗi xuất dữ liệu: {str(e)}"
        )
    

@router.get("/name", 
            response_model=ListAuthorNameResponse,
            status_code=status.HTTP_200_OK)
async def get_author_names(
        db: Session = Depends(get_db), 
    ):

    try:
        authors = db.query(Author).all()
        authors_name_res = ListAuthorNameResponse(
            authors=[AuthorName(id=a.id, name=a.name) for a in authors]
        )

        return authors_name_res
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/{id}",
            response_model=AuthorResponse)
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
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"author": author}
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/search",
            response_model=AuthorPageableResponse, 
            status_code=status.HTTP_200_OK)
async def search_authors(
        info: AuthorSearch,
        page: int,
        page_size: int,
        db: Session = Depends(get_db)
    ):

    try:
        authors = db.query(Author)
        if info.name and info.name.strip():
            authors = authors.filter(func.lower(Author.name).like(f"%{info.name.strip().lower()}%"))
        if info.birthdate:
            authors = authors.filter(Author.birthdate == info.birthdate)
        if info.address and info.address.strip():
            authors = authors.filter(func.lower(Author.address).like(f"%{info.address.strip().lower()}%"))
        if info.pen_name and info.pen_name.strip():
            authors = authors.filter(func.lower(Author.pen_name).like(f"%{info.pen_name.strip().lower()}%"))
        if info.biography and info.biography.strip():
            authors = authors.filter(func.lower(Author.biography).like(f"%{info.biography.strip().lower()}%"))

        total_count = authors.count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        authors = authors.offset(offset).limit(page_size).all()

        return AuthorPageableResponse(
            authors=authors,
            total_pages=total_pages,
            total_data=total_count
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/create",
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

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Tạo tác giả thành công"}
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
async def import_author(
        file: UploadFile,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    COLUMN_MAPPING = {
        "Tên tác giả": "name",
        "Ngày sinh": "birthdate",
        "Địa chỉ": "address",
        "Bút danh": "pen_name",
        "Tiểu sử": "biography"
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
    
    existing_author_names = {a.name for a in db.query(Author).all()}
    existing_author_dates = {a.birthdate for a in db.query(Author).all()}
    errors = []
    list_authors = []
    
    for index, row in df.iterrows():
        name = row.get("name")
        if not name:
            errors.append({"Dòng": index + 2, "Lỗi": "Tên tác giả không được để trống."})
            continue
        
        date = row.get("birthdate")
        if name in existing_author_names and date and date in existing_author_dates:
            errors.append({"Dòng": index + 2, "Lỗi": f"Tác giả '{name}' đã tồn tại."})
            continue
        
        birthdate = None if pd.isna(row.get("birthdate")) else str(row.get("birthdate"))
        address = None if pd.isna(row.get("address")) else row.get("address")
        pen_name = None if pd.isna(row.get("pen_name")) else row.get("pen_name")
        biography = None if pd.isna(row.get("biography")) else row.get("biography")
        
        author = Author(
            name=name,
            birthdate=birthdate,
            address=address,
            pen_name=pen_name,
            biography=biography
        )
        list_authors.append(author)
    
    if errors:
        return JSONResponse(
            status_code=400,
            content={"errors": errors}
        )
    
    try:
        db.bulk_save_objects(list_authors)
        db.commit()
        return JSONResponse(
            status_code=201,
            content={"message": "Import tác giả thành công"}
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
            status_code=500, 
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
        
        author.update(
            new_author.dict(), 
            synchronize_session=False
        )
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Cập nhật tác giả thành công"}
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

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa tác giả thành công"}
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
async def delete_authors(
        ids: AuthorDelete,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        authors = db.query(Author).filter(Author.id.in_(ids.list_id))
        if not authors.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tác giả không tồn tại"
            )

        authors.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa danh sách tác giả thành công"}
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
async def delete_all_authors(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        db.query(Author).delete()
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa tất cả tác giả thành công"}
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
