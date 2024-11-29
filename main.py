import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from configs.database import Base, engine
from configs.conf import settings
from role.routers import role
from user_info.routers import user_info
from user_account.routers import user_account
from user_role.routers import user_role
from authen.routers import authen
from author.routers import author
from category.routers import category
from publisher.routers import publisher
from book.routers import book
from borrow.routers import borrow



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
app.router.include_router(user_info.router)
app.router.include_router(user_account.router)
app.router.include_router(user_role.router)
app.router.include_router(authen.router)
app.router.include_router(author.router)
app.router.include_router(category.router)
app.router.include_router(publisher.router)
app.router.include_router(book.router)
app.router.include_router(borrow.router)


# if __name__ == "__main__":
#     uvicorn.run(app, host=settings.host, port=settings.port)
    