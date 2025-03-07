from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import func, extract
from sqlalchemy.orm import Session
from book_copy.models.book_copy import BookCopy
from configs.authentication import get_current_user
from configs.database import get_db
from book.models.book import Book
from role.models.role import Role
from user.models.user import User
from borrow.models.borrow import Borrow
from stats.schemas.stats import *
from user_role.models.user_role import UserRole
from category.models.category import Category

router = APIRouter(
    prefix="/stats",
    tags=["Stats"],
)

@router.get("/", response_model=StatsResponse)
def get_library_stats(
        db: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)
    ):
        
    try:
        is_admin = db.query(User)\
            .join(UserRole)\
            .join(Role)\
            .filter(User.id == current_user.id, 
                    Role.name == "admin").first()
        
        if not is_admin:
            return JSONResponse(
                content={"error": "You are not authorized to access this resource."}, 
                status_code=status.HTTP_403_FORBIDDEN
            )

        total_books = db.query(BookCopy).count()
        total_borrowings = db.query(Borrow).count()
        borrowed_books = db.query(Borrow).filter(Borrow.status.in_(["Quá hạn", "Đang mượn"])).count()
        active_users = db.query(User).count()

        return {
            "total_books": total_books,
            "total_borrows": total_borrowings, 
            "borrowed_books": borrowed_books,
            "active_users": active_users
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, 
            content={"error": str(e)}
        )


@router.get("/monthly", 
            response_model=MonthlyBorrowsResponse)
def get_monthly_borrowing_stats(
        db: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)
    ):

    try:
        is_admin = db.query(User)\
            .join(UserRole)\
            .join(Role)\
            .filter(User.id == current_user.id, 
                    Role.name == "admin").first()
        
        if not is_admin:
            return {"error": "You are not authorized to access this resource."}

        today = datetime.today()
        last_6_months = today - timedelta(days=180)

        results = (
            db.query(func.date_trunc('month', Borrow.created_at), func.count())
            .filter(Borrow.created_at >= last_6_months)
            .group_by(func.date_trunc('month', Borrow.created_at))
            .order_by(func.date_trunc('month', Borrow.created_at))
            .all()
        )

        return JSONResponse(
            content={
                "monthly_borrows": [{"month": month.strftime("%Y-%m"), "count": count} for month, count in results]
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )


@router.get("/top-books", response_model=TopBooksResponse)
def get_top_borrowed_books(
        db: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)
    ):
    try:
        is_admin = db.query(User)\
            .join(UserRole)\
            .join(Role)\
            .filter(User.id == current_user.id, 
                    Role.name == "admin").first()
        
        if not is_admin:
            return {"error": "You are not authorized to access this resource."}
        
        results = (
            db.query(Book.name, func.count(Borrow.id))
            .join(BookCopy, BookCopy.book_id == Book.id)
            .join(Borrow, Borrow.book_copy_id == BookCopy.id)  # Fixed join condition
            .group_by(Book.id)
            .order_by(func.count(Borrow.id).desc())
            .limit(10)
            .all()
        )

        return JSONResponse(
            content={
                "top_books": [{"name": name, "count": count} for name, count in results]
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        raise HTTPException(
            status_code=409, 
            detail=str(e)
        )

@router.get("/books/by-category", response_model=CategoryStatsResponse)
def get_books_by_category(
        db: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)
    ):
    try:
        is_admin = db.query(User)\
            .join(UserRole)\
            .join(Role)\
            .filter(User.id == current_user.id, 
                    Role.name == "admin").first()
        
        if not is_admin:
            return JSONResponse(
                content={"error": "You are not authorized to access this resource."},
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        results = (
            db.query(Category.name, func.count(Book.id))
            .join(Book, Book.category_id == Category.id)
            .group_by(Category.name)
            .order_by(func.count(Book.id).desc())
            .all()
        )

        return JSONResponse(
            content={
                "categories": [{"name": name, "count": count} for name, count in results]
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        raise HTTPException(
            status_code=409, 
            detail=str(e)
        )


@router.get("/books/status", response_model=BookStatusResponse)
def get_books_by_status(
        db: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)
    ):
    try:
        is_admin = db.query(User)\
            .join(UserRole)\
            .join(Role)\
            .filter(User.id == current_user.id, 
                    Role.name == "admin").first()
        
        if not is_admin:
            return JSONResponse(
                content={"error": "You are not authorized to access this resource."},
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        total_books = db.query(func.count(BookCopy.id)).scalar()
        
        borrowed_counts = (
            db.query(Borrow.status, func.count(BookCopy.id))
            .join(BookCopy, BookCopy.id == Borrow.book_copy_id)
            .filter(Borrow.status.in_(["Đang mượn", "Quá hạn"]))
            .group_by(Borrow.status)
            .all()
        )
        
        borrowed_total = sum(count for _, count in borrowed_counts)
        available_books = total_books - borrowed_total
        
        status_counts = [{"status": "Có sẵn", "count": available_books}]
        status_counts.extend([{"status": status, "count": count} for status, count in borrowed_counts])
        
        return JSONResponse(
            content={
                "status_counts": status_counts
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        raise HTTPException(
            status_code=409, 
            detail=str(e)
        )

@router.get("/borrowing/monthly", response_model=MonthlyTrendsResponse)
def get_monthly_borrowing_trends(
        db: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)
    ):
    try:
        is_admin = db.query(User)\
            .join(UserRole)\
            .join(Role)\
            .filter(User.id == current_user.id, 
                    Role.name == "admin").first()
        
        if not is_admin:
            return JSONResponse(
                content={"error": "You are not authorized to access this resource."},
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Get last 5 months
        today = datetime.today()
        last_5_months = today - timedelta(days=150)
        
        # Query for borrowed books by month
        borrowed_by_month = (
            db.query(
                func.to_char(Borrow.created_at, 'MM/YYYY').label('month'),
                func.count().label('count')
            )
            .filter(Borrow.created_at >= last_5_months)
            .group_by(func.to_char(Borrow.created_at, 'MM/YYYY'))
            .all()
        )
        
        # Query for returned books by month
        returned_by_month = (
            db.query(
                func.to_char(Borrow.return_date, 'MM/YYYY').label('month'),
                func.count().label('count')
            )
            .filter(
                Borrow.return_date.isnot(None),
                Borrow.return_date >= last_5_months
            )
            .group_by(func.to_char(Borrow.return_date, 'MM/YYYY'))
            .all()
        )
        
        # Create month-based dictionary for easier data manipulation
        borrowed_dict = {month: count for month, count in borrowed_by_month}
        returned_dict = {month: count for month, count in returned_by_month}
        
        # Get all months in the period
        all_months = set(borrowed_dict.keys()) | set(returned_dict.keys())
        
        # Create final result
        result = [
            {
                "month": month,
                "borrowed": borrowed_dict.get(month, 0),
                "returned": returned_dict.get(month, 0)
            }
            for month in sorted(all_months)
        ]
        
        return JSONResponse(
            content={"data": result},
            status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )

@router.get("/borrowing/by-day", response_model=BorrowingByDayResponse)
def get_borrowing_by_day(
        db: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)
    ):
    try:
        is_admin = db.query(User)\
            .join(UserRole)\
            .join(Role)\
            .filter(User.id == current_user.id, 
                    Role.name == "admin").first()
        
        if not is_admin:
            return JSONResponse(
                content={"error": "You are not authorized to access this resource."},
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Query borrowings grouped by day of week (1-7, where 1 is Monday)
        results = (
            db.query(
                extract('dow', Borrow.created_at).label('dow'),
                func.count().label('count')
            )
            .group_by('dow')
            .order_by('dow')
            .all()
        )
        
        # Map day of week number to Vietnamese day names
        day_names = {
            1: "Thứ 2", 
            2: "Thứ 3", 
            3: "Thứ 4", 
            4: "Thứ 5", 
            5: "Thứ 6", 
            6: "Thứ 7", 
            0: "Chủ nhật"  # Sunday is 0 in PostgreSQL's extract(dow)
        }
        
        # Create final result including all days
        day_counts = {day_name: 0 for day_name in day_names.values()}
        for dow, count in results:
            day_name = day_names.get(dow, f"Day {dow}")
            day_counts[day_name] = count
        
        result = [{"day": day, "count": count} for day, count in day_counts.items()]
        # Sort in the correct order of days
        correct_order = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
        result.sort(key=lambda x: correct_order.index(x["day"]))
        
        return JSONResponse(
            content={"data": result},
            status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )

@router.get("/borrowing/status", response_model=ReturnStatusResponse)
def get_return_status(
        db: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)
    ):
    try:
        is_admin = db.query(User)\
            .join(UserRole)\
            .join(Role)\
            .filter(User.id == current_user.id, 
                    Role.name == "admin").first()
        
        if not is_admin:
            return JSONResponse(
                content={"error": "You are not authorized to access this resource."},
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Count on-time returns
        on_time_returns = (
            db.query(func.count())
            .filter(
                Borrow.return_date <= Borrow.due_date,
                Borrow.return_date.isnot(None)
            )
            .scalar() or 0
        )
        
        # Count late returns
        late_returns = (
            db.query(func.count())
            .filter(
                Borrow.return_date > Borrow.due_date
            )
            .scalar() or 0
        )
        
        # Count not returned yet
        not_returned = (
            db.query(func.count())
            .filter(
                Borrow.return_date.is_(None),
                Borrow.status.in_(["Đang mượn", "Quá hạn"])
            )
            .scalar() or 0
        )
        
        result = [
            {"status": "Đúng hạn", "value": on_time_returns},
            {"status": "Trễ hạn", "value": late_returns},
            {"status": "Chưa trả", "value": not_returned}
        ]
        
        return JSONResponse(
            content={"data": result},
            status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )



