from fastapi import status, APIRouter, Depends
from .. import schemas, database, oauth2
from ..repository import user
from sqlalchemy.orm import Session


router = APIRouter(
    prefix= "/user",
    tags=["Users"]
)


@router.post("/register", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.UserResponse)
async def create_user(user_info: schemas.UserCreate, 
                      db: Session = Depends(database.get_db)):
    
    return user.create_user(user_info, db)


# @router.get("/{id}", 
#             response_model=schemas.UserResponse)
# async def get_user_byid(id: int, 
#                         db: Session = Depends(database.get_db)):
    
#     return user.get_user_byid(id, db)


# @router.put("/update_info", 
#             response_model=schemas.UserResponse)
# async def updateUser(newUser: schemas.UserUpdate, 
#                      db: Session = Depends(database.get_db), 
#                      current_user = Depends(oauth2.get_current_user)):

#     return user.updateUser(newUser, db, current_user)


# @router.put("/update_pwd")
# async def updateUser(new_pwd: schemas.UserRePwd, 
#                      db: Session = Depends(database.get_db), 
#                      current_user = Depends(oauth2.get_current_user)):

#     return user.re_pwd(new_pwd, db, current_user)