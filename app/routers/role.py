from fastapi import status, Depends, APIRouter
from .. import schemas, database, oauth2
from sqlalchemy.orm import Session
from ..repository import role


router = APIRouter(
    prefix="/admin",
    tags=["Roles"]
)

@router.post("/create_role", 
             status_code=status.HTTP_201_CREATED)
async def create_role(new_role: schemas.RoleCreate, 
                      db: Session = Depends(database.get_db), 
                      current_user: int = Depends(oauth2.get_current_user)):
    
    return role.create_role(new_role, db, current_user)


# @router.post("/assign_role", 
#              status_code=status.HTTP_200_OK)
# async def assign_role(assign_info: schemas.RoleAssign, 
#                       db: Session = Depends(database.get_db), 
#                       current_user: int = Depends(oauth2.get_current_user)):
    
#     return role.assign_role(assign_info, db, current_user)
      

@router.delete("/delete_role/{role_id}", 
               status_code=status.HTTP_202_ACCEPTED)
async def delete_role(role_id: int, 
                      db: Session = Depends(database.get_db), 
                      current_user: int = Depends(oauth2.get_current_user)):
    
    return role.delete_role(role_id, db, current_user)