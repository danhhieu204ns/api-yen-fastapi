from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
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
            return {"error": "You are not authorized to access this resource."}

        total_books = db.query(Book).count()
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
        return {"error": str(e)}


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

        return {
            "monthly_borrows": [{"month": str(month), "count": count} for month, count in results]
        }

    except Exception as e:
        raise HTTPException(
            status_code=409, 
            detail=str(e)
        )


@router.get("/top-books", 
            response_model=TopBooksResponse)
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

        return {
            "top_books": [{"name": name, "count": count} for name, count in results]
        }

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
            return {"error": "You are not authorized to access this resource."}
        
        results = (
            db.query(Category.name, func.count(Book.id))
            .join(Book, Book.category_id == Category.id)
            .group_by(Category.name)
            .order_by(func.count(Book.id).desc())
            .all()
        )

        return {
            "categories": [{"category": name, "count": count} for name, count in results]
        }

    except Exception as e:
        raise HTTPException(
            status_code=409, 
            detail=str(e)
        )

@router.get("/books/most-borrowed", response_model=TopBooksResponse)
def get_most_borrowed_books(
        db: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user),
        limit: int = 10
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
            .join(Borrow, Borrow.book_copy_id == BookCopy.id)
            .group_by(Book.id, Book.name)
            .order_by(func.count(Borrow.id).desc())
            .limit(limit)
            .all()
        )

        return {
            "top_books": [{"name": name, "count": count} for name, count in results]
        }

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
            return {"error": "You are not authorized to access this resource."}
        
        # Count total books
        total_books = db.query(func.count(BookCopy.id)).scalar()
        
        # Count books by borrow status
        borrowed_counts = (
            db.query(Borrow.status, func.count(BookCopy.id))
            .join(BookCopy, BookCopy.id == Borrow.book_copy_id)
            .filter(Borrow.status.in_(["Đang mượn", "Quá hạn"]))
            .group_by(Borrow.status)
            .all()
        )
        
        # Calculate available books
        borrowed_total = sum(count for _, count in borrowed_counts)
        available_books = total_books - borrowed_total
        
        # Prepare result
        status_counts = [{"status": "Có sẵn", "count": available_books}]
        status_counts.extend([{"status": status, "count": count} for status, count in borrowed_counts])
        
        return {
            "statuses": status_counts
        }

    except Exception as e:
        raise HTTPException(
            status_code=409, 
            detail=str(e)
        )


