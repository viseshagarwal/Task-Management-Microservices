from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic_settings import BaseSettings
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from urllib.parse import quote_plus
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx

username = "<username>"
password = "<database password>"
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)


# Settings
class Settings(BaseSettings):
    SECRET_KEY: str = "mysecretkey"  # Replace with your secret key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MONGO_DETAILS: str = (
        f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.xyz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    )


settings = Settings()

# Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    password: str


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = AsyncIOMotorClient(settings.MONGO_DETAILS)
database = client["FastAPI-Task-Management"]
task_collection = database.get_collection("tasks")
user_collection = database.get_collection("users")


NODE_API_URL = "https://protected-citadel-28892-9b3d80cc590b.herokuapp.com/api"


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[datetime] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await user_collection.find_one({"username": token_data.username})
    if user is None:
        raise credentials_exception
    return user


# Models
class Task(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: Optional[str] = "medium"  # Added priority
    deadline: Optional[datetime] = None  # Added deadline
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class TaskInDB(Task):
    id: str


async def assign_task_to_user(task_id: str, user_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{NODE_API_URL}/tasks/assign",
            json={"task_id": task_id, "user_id": user_id},
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail="Failed to assign task"
            )


@app.post("/tasks/", response_model=TaskInDB)
async def create_task(task: Task, current_user: User = Depends(get_current_user)):
    task_data = task.dict()
    task_data["created_at"] = datetime.now()
    task_data["updated_at"] = datetime.now()
    task_data["user_id"] = current_user["_id"]
    new_task = await task_collection.insert_one(task_data)
    created_task = await task_collection.find_one({"_id": new_task.inserted_id})
    created_task["id"] = str(created_task["_id"])
    return TaskInDB(**created_task)


@app.get("/tasks/", response_model=List[TaskInDB])
async def get_tasks(current_user: User = Depends(get_current_user)):
    tasks = await task_collection.find({"user_id": current_user["_id"]}).to_list(100)
    for task in tasks:
        task["id"] = str(task["_id"])  # Convert ObjectId to string and add 'id' field
    return tasks


# Get Task by ID
@app.get("/tasks/{task_id}", response_model=TaskInDB)
async def get_task(task_id: str, current_user: User = Depends(get_current_user)):
    task = await task_collection.find_one(
        {"_id": ObjectId(task_id), "user_id": current_user["_id"]}
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskInDB(**task)


# Update Task
@app.put("/tasks/{task_id}", response_model=TaskInDB)
async def update_task(
    task_id: str, task: Task, current_user: User = Depends(get_current_user)
):
    task_data = task.dict()
    task_data["updated_at"] = datetime.now()
    updated_task = await task_collection.find_one_and_update(
        {"_id": ObjectId(task_id), "user_id": current_user["_id"]},
        {"$set": task_data},
        return_document=True,
    )
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskInDB(**updated_task)


# Delete Task
@app.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(task_id: str, current_user: User = Depends(get_current_user)):
    delete_result = await task_collection.delete_one(
        {"_id": ObjectId(task_id), "user_id": current_user["_id"]}
    )
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


# Token endpoint for authentication
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_collection.find_one({"username": form_data.username})
    if user is None or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register/")
async def register(user: User):
    existing_user = await user_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["hashed_password"] = hashed_password
    await user_collection.insert_one(user_dict)
    return {"msg": "User registered successfully"}
