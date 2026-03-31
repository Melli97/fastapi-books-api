from typing import Annotated  # Importa Annotated per annotare il tipo di dipendenze
from sqlalchemy.orm import Session  # Importa la classe Session da SQLAlchemy per gestire le sessioni del database
from fastapi import FastAPI, Depends  # Importa FastAPI per creare l'app e Depends per gestire le dipendenze
import models  # Importa il modulo models, che contiene i modelli del database
from models import Todos  # Importa il modello Todos dal modulo models
from database import engine, SessionLocal  # Importa l'engine del database e la classe di sessione locale

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
@app.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all()  # Esegue una query per ottenere tutte le voci nella tabella Todos



