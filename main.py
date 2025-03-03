from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from configs.database import Base, engine
from configs.conf import settings
from role.routers import role
from permission.routers import permission
from role_permission.routers import role_permission
from user.routers import user
from auth_credential.routers import auth_credential
from user_role.routers import user_role
from authen.routers import authen
from author.routers import author
from category.routers import category
from publisher.routers import publisher
from book.routers import book
from book_copy.routers import book_copy
from bookshelf.routers import bookshelf
from borrow.routers import borrow
from stats.routers import stats
import uvicorn


Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.router.include_router(role.router)
app.router.include_router(permission.router)
app.router.include_router(role_permission.router)
app.router.include_router(user.router)
app.router.include_router(auth_credential.router)
app.router.include_router(user_role.router)
app.router.include_router(authen.router)
app.router.include_router(author.router)
app.router.include_router(category.router)
app.router.include_router(publisher.router)
app.router.include_router(book.router)
app.router.include_router(bookshelf.router)
app.router.include_router(book_copy.router)
app.router.include_router(borrow.router)
app.router.include_router(stats.router)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
    
