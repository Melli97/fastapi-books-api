from typing import Annotated
from sqlalchemy.orm import Session  # Importa la classe Session da SQLAlchemy per gestire le sessioni del database
from fastapi import FastAPI, APIRouter,Depends # Importa FastAPI APIRouter per creare gruppi di endpoint
from pydantic import BaseModel
from database import  SessionLocal  # Importa l'engine del database e la classe di sessione locale
from models import Users
from passlib.context import CryptContext #importare per criptare
from starlette import status

router = APIRouter()
# Crea un router: serve per organizzare gli endpoint in moduli separati
bcypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')



class CreateUserRequest(BaseModel):
    username : str
    email: str
    first_name : str
    last_name : str
    password : str
    role : str



# Funzione per ottenere una sessione del database
def get_db():
    db = SessionLocal()  # Crea una nuova sessione del database
    try:
        yield db  # Restituisce la sessione per l'uso
    finally:
        db.close()  # Assicura che la sessione venga chiusa al termine dell'uso

# Annotazione per la dipendenza del database
db_dependency = Annotated[Session, Depends(get_db)]



@router.post("/auth", status_code= status.HTTP_201_CREATED)
# Definisce un endpoint GET sul percorso /auth/
# Questo endpoint sarà accessibile quando il router viene incluso nell'app principale
async def create_user(db: db_dependency ,
                      create_user_request: CreateUserRequest):
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name =create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = bcypt_context.hash(create_user_request.password), #per criptare passsword
        is_active = True
    )
    db.add(create_user_model)
    db.commit()



#per cryptare password scaricare dipendenze pip install passlib e scaricare dipendenza pip install bcrypt==4.0.1