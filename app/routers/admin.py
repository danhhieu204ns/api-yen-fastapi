from fastapi import status, APIRouter, Depends
from .. import schemas, database, oauth2
from ..repository import admin
from sqlalchemy.orm import Session


router = APIRouter(
    prefix= "/admin",
    tags=["Admins"]
)


@router.post("/register", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.UserResponse)
async def create_user(user_info: schemas.UserCreate, 
                      db: Session = Depends(database.get_db)):
    
    return user.create_user(user_info, db)


@router.get("/all", 
            status_code=status.HTTP_200_OK, 
            response_model=list[schemas.UserResponse])
async def get_all_admin(db: Session = Depends(database.get_db), 
                        current_user = Depends(oauth2.get_current_user)):
    
    return admin.get_all_admin(db, current_user)


@router.get("/{id}", 
            status_code=status.HTTP_200_OK, 
            response_model=schemas.UserResponse)
async def get_admin_by_id(id: int, 
                          db: Session = Depends(database.get_db), 
                          current_user = Depends(oauth2.get_current_user)):
    
    return admin.get_admin_by_id(id, db, current_user)


# @router.put("/update_info", 
#             response_model=schemas.UserResponse)
# async def updateUser(newUser: schemas.UserUpdate, 
#                      db: Session = Depends(database.get_db), 
#                      current_user = Depends(oauth2.get_current_user)):

#     return user.updateUser(newUser, db, current_user)


@router.put("/update_pwd")
async def updateUser(new_pwd: schemas.UserRePwd, 
                     db: Session = Depends(database.get_db), 
                     current_user = Depends(oauth2.get_current_user)):

    return user.re_pwd(new_pwd, db, current_user)