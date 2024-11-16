import uuid
import time
from fastapi import FastAPI, HTTPException, status, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from eg_db import user_db

app = FastAPI()

class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    age: int
    height: float


@app.post("/create_user/", status_code=status.HTTP_201_CREATED)
async def create_user(
    new_user: User = Body(title="Creating a new user"), new_user_id=str(uuid.uuid4())
):

    for _, users in user_db.items():
        if (
            users.get("email") == new_user.email
            or users.get("first_name") == new_user.first_name
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or first name already registered",
            )
    user_db[new_user_id] = new_user.model_dump()
    return user_db[new_user_id]


@app.get("/get_users/")
async def get_users():
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No users found"
        )
    return user_db


# CORSMiddleware
origins = ["http://localhost:8080"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
    max_age=600,
)


# logger
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["Time_taken"] = str(process_time)
    return response
