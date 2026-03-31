from typing import Annotated  # Importa Annotated per annotare il tipo di dipendenze
from sqlalchemy.orm import Session  # Importa la classe Session da SQLAlchemy per gestire le sessioni del database
from fastapi import FastAPI, Depends, HTTPException, Path  # Importa FastAPI per creare l'app e Depends per gestire le dipendenze
import models  # Importa il modulo models, che contiene i modelli del database
from models import Todos  # Importa il modello Todos dal modulo models
from database import engine, SessionLocal  # Importa l'engine del database e la classe di sessione locale
from starlette import status
# Crea un'istanza dell'app FastAPI
app = FastAPI()

# Crea le tabelle nel database utilizzando i modelli definiti
models.Base.metadata.create_all(bind=engine)

# Funzione per ottenere una sessione del database
def get_db():
    db = SessionLocal()  # Crea una nuova sessione del database
    try:
        yield db  # Restituisce la sessione per l'uso
    finally:
        db.close()  # Assicura che la sessione venga chiusa al termine dell'uso

# Annotazione per la dipendenza del database
db_dependency = Annotated[Session, Depends(get_db)]

# Endpoint per leggere tutte le voci dalla tabella Todos
@app.get("/", status_code= status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()  # Esegue una query per ottenere tutte le voci nella tabella Todos


@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)  # Se la richiesta ha successo, restituisce HTTP 200

async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    # db: viene iniettato automaticamente tramite la dependency (sessione DB)
    # todo_id: parametro preso dall'URL
    # Path(gt=0): valida che todo_id sia > 0

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    # Query al database:
    # - cerca nella tabella Todos
    # - filtra per id uguale a todo_id
    # - prende il primo risultato trovato (oppure None se non esiste)

    if todo_model is not None:
        return todo_model     # Se il todo esiste, lo restituisce come risposta
   
    raise HTTPException(status_code=404, detail='todo non trovato')
    # Se non esiste nessun record con quell'id:
    # - restituisce errore 404 (Not Found)

