from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import auth, role, admin, user, author, publisher, genre, bookgroup, book, borrow


models.Base.metadata.create_all(bind=engine)

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

app.include_router(auth.router)
app.include_router(role.router)
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(author.router)
app.include_router(publisher.router)
app.include_router(genre.router)
app.include_router(bookgroup.router)
app.include_router(book.router)
app.include_router(borrow.router)

