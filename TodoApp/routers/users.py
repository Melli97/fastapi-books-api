from typing import Annotated  # Serve per tipizzare le dipendenze in FastAPI
from pydantic import BaseModel, Field  # Per creare modelli di validazione dati
from sqlalchemy.orm import Session  # Per gestire la sessione del database
from fastapi import APIRouter, Depends, HTTPException, Path  # Strumenti FastAPI
from models import Todos, Users  # Modelli del database
from database import SessionLocal  # Sessione DB locale
from starlette import status  # Codici di stato HTTP
from .auth import get_current_user  # Funzione per ottenere utente autenticato
from passlib.context import CryptContext  # Per hashare le password

# ===== ROUTER =====
# Crea un gruppo di endpoint con prefisso /users
router = APIRouter(
    prefix='/users',
    tags=['users']
)

# ===== DATABASE =====
# Funzione per ottenere una sessione del database
def get_db():
    db = SessionLocal()  # Crea una nuova connessione al DB
    try:
        yield db  # Restituisce la sessione all'endpoint
    finally:
        db.close()  # Chiude la connessione dopo l'uso

# Dependency per il database
db_dependency = Annotated[Session, Depends(get_db)]

# Dependency per l'utente autenticato (presa dal token)
user_dependency = Annotated[dict, Depends(get_current_user)]

# ===== HASH PASSWORD =====
# Configura bcrypt per criptare le password
bcypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# ===== MODELLO PER CAMBIO PASSWORD =====
class UserVerification(BaseModel):
    password: str  # vecchia password
    new_password: str = Field(min_length=6)  # nuova password (min 6 caratteri)

# ===== GET USER =====
# Restituisce i dati dell'utente autenticato
@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):

    # Se non c'è utente autenticato → errore
    if user is None:
        raise HTTPException(status_code=401, detail='Autenticazione fallita')

    # Cerca l'utente nel DB usando l'id preso dal token
    return db.query(Users).filter(Users.id == user.get('id')).first()

# ===== CAMBIO PASSWORD =====
@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: user_dependency,           # utente autenticato
    db: db_dependency,               # connessione DB
    user_verification: UserVerification  # dati inviati (vecchia + nuova password)
):

    # Se non autenticato → errore
    if user is None:
        raise HTTPException(status_code=401, detail='Autenticazione fallita')

    # Prende l'utente dal database
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    # Verifica che la password inserita sia corretta
    if not bcypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Errore sulla password')

    # Se la password è corretta → aggiorna con la nuova (hashata)
    user_model.hashed_password = bcypt_context.hash(user_verification.new_password)

    # Salva nel database
    db.add(user_model)
    db.commit()



@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency , phone_number: str):

    if user is None:
        raise HTTPException(status_code=401, detail='Autenticazione fallita')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()