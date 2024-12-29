from fastapi import APIRouter, HTTPException
from ..schemas.user import UserCreate, UserResponse
from ...database.db_manager import DatabaseManager

router = APIRouter()
db_manager = DatabaseManager()

@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    try:
        user_id = db_manager.create_user(user.username, user.email)
        return UserResponse(id=user_id, username=user.username, email=user.email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))