from typing import Annotated

from fastapi import FastAPI, Body, Depends
from sqlalchemy.orm import Session

from app import model
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import sign_jwt
from app.db import SessionLocal, engine
from app.model import PostSchema, UserSchema, UserLoginSchema, Post, User


def get_db():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()

db_dependency = Annotated[Session,Depends(get_db)]

posts = [
    {
        "id": 1,
        "title": "Pancake",
        "content": "Lorem Ipsum ..."
    }
]

users = []

app = FastAPI()

model.Base.metadata.create_all(bind=engine)
# helpers
@app.get("/check_db")
def test(db:db_dependency):
    post = Post(title="hello")
    db.add(post)
    db.commit()
    return {"response":db.query(Post).all()}

def check_user(data: UserLoginSchema,db:db_dependency):
    for user in db.query(User).all():
        if user.email == data.email and user.password == data.password:
            return True
    return False


# route handlers

@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your blog!"}


@app.get("/posts", tags=["posts"])
async def get_posts(db:db_dependency):
    return { "data": db.query(Post).all() }


@app.post("/user/signup", tags=["user"])
async def create_user(db:db_dependency,user: UserSchema = Body(...)):
    user_created = User(username=user.fullname,password = user.password, email=user.email)
    db.add(user_created)
    db.commit()# replace with db call, making sure to hash the password first
    return sign_jwt(user.email)



@app.get("/posts/{id}", tags=["posts"])
async def get_single_post(id: int,db:db_dependency) -> dict:

    post = db.query(Post).filter(Post.id == id).all()
    if post:
        return post
    else:
        return {"message": "Post not found"}


@app.post("/posts", dependencies=[Depends(JWTBearer())], tags=["posts"])
async def add_post(post: PostSchema , db:db_dependency):
    post_created = Post(title= post.title)
    db.add(post_created)
    db.commit()
    return {
        "data": "post added."
    }


@app.post("/user/login", tags=["user"])
async def user_login(db:db_dependency ,user: UserLoginSchema = Body(...)):
    if check_user(user,db):
        return sign_jwt(user.email)
    return {
        "error": "Wrong login details!"
    }
