from fastapi import FastAPI, APIRouter # Importa FastAPI APIRouter per creare gruppi di endpoint
from pydantic import BaseModel
from models import Users

router = APIRouter()
# Crea un router: serve per organizzare gli endpoint in moduli separati

class CreateUserRequest(BaseModel):
    username : str
    email: str
    first_name : str
    last_name : str
    password : str
    role : str




@router.post("/auth")
# Definisce un endpoint GET sul percorso /auth/
# Questo endpoint sarà accessibile quando il router viene incluso nell'app principale

async def create_user(create_user_request: CreateUserRequest):
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name =create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = create_user_request.password,
        is_active = True
    )
    return create_user_model

