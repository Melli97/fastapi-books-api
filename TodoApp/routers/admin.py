from typing import Annotated  # Serve per tipizzare le dipendenze (FastAPI moderno)
from pydantic import BaseModel, Field  # Validazione dati (qui non usato ma importato)
from sqlalchemy.orm import Session  # Gestione sessione database
from fastapi import APIRouter, Depends, HTTPException, Path  # Strumenti FastAPI
from models import Todos  # Modello della tabella Todos
from database import SessionLocal  # Connessione al database
from starlette import status  # Codici HTTP
from .auth import get_current_user  # Funzione che legge il token JWT

# ===== ROUTER =====
# Crea gruppo endpoint con prefisso /admin
router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

# ===== DATABASE =====
# Funzione per ottenere una sessione DB
def get_db():
    db = SessionLocal()  # apre connessione
    try:
        yield db  # passa la connessione all'endpoint
    finally:
        db.close()  # chiude connessione

# Dependency DB
db_dependency = Annotated[Session, Depends(get_db)]

# Dependency utente autenticato (preso dal token)
user_dependency = Annotated[dict, Depends(get_current_user)]

# ===== GET TUTTI I TODO =====
@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):

    # Controllo autenticazione + ruolo admin
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail='autenticazione fallita')

    # Restituisce tutti i todo dal database
    return db.query(Todos).all()

# ===== DELETE TODO =====
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency,         # utente autenticato
    db: db_dependency,             # connessione DB
    todo_id: int = Path(gt=0)      # id del todo (deve essere > 0)
):

    # Controllo autenticazione + admin
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail='autenticazione fallita')

    # Cerca il todo nel database
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    # Se non esiste → errore 404
    if todo_model is None:
        raise HTTPException(status_code=404, detail='todo non trovato')

    # Cancella il record dal database
    db.query(Todos).filter(Todos.id == todo_id).delete()

    # Salva le modifiche (DELETE reale)
    db.commit()