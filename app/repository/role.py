from fastapi import status, HTTPException
from .. import schemas, models, utils
from sqlalchemy.orm import Session


def create_role(new_role: schemas.RoleCreate, 
                db: Session, 
                current_user):
    
    if current_user.role_id != utils.get_role_by_name(db, "superadmin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    if utils.get_role_by_name(db, new_role.name):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Role already exist")
    
    db.add(models.Role(**new_role.dict()))
    db.commit()
    return {"message": "create role succesful"}


# def assign_role(assign_info: schemas.RoleAssign,
#                 db: Session, 
#                 current_user):
    
#     role = utils.get_role_by_name(db, models, assign_info.role_name)
#     if not role:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
#                             detail="Not found role")
    
#     user = utils.get_user_by_id(db, models, assign_info.user_id)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
#                             detail="Not found user")


#     return {"message": "create role succesful"}


def delete_role(role_id: int,
                db: Session, 
                current_user):
    
    if current_user.role_id != utils.get_role_by_name(db, "superadmin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")

    role_query = utils.query_role_by_id(db, role_id)
    
    role_query.delete(synchronize_session=False)
    db.commit()

    return {"message": "delete role succesful"}
