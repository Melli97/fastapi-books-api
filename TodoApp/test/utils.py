from sqlalchemy import  create_engine, text
from sqlalchemy.pool import StaticPool
from database import Base
from main import app
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import pytest
from models import Todos
# ==========================================
# CONFIGURAZIONE AMBIENTE E DATABASE DI TEST
# ==========================================
# Imposta l'URL per il database di test (SQLite su file)
SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db' 

# Crea il motore del database configurato per i test
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False}, # Necessario per SQLite
    poolclass=StaticPool # Mantiene la connessione aperta per tutta la durata del test
)

# Crea la factory per le sessioni di test
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea fisicamente le tabelle nel database di test
Base.metadata.create_all(bind=engine)

# ==========================================
# OVERRIDE DELLE DIPENDENZE (MOCKING)
# ==========================================

# Funzione che sostituisce il 'get_db' originale per iniettare il db di test
def ovveride_get_db():
    db = TestingSessionLocal() 
    try:
        yield db  # Fornisce la sessione al test
    finally:
        db.close()  # Chiude la sessione dopo il test

# Funzione che simula un utente loggato senza dover passare per il login reale
# Funzione che simula un utente loggato
def override_get_current_user():
    # Il tuo admin.py cerca 'role', quindi dobbiamo passare 'role'
    return {'username': 'Mancio997', 'id': 1, 'role': 'admin'}

# Crea il client per fare chiamate HTTP fittizie all'app
client = TestClient(app)

# ==========================================
# FIXTURE PER LA GESTIONE DATI
# ==========================================

@pytest.fixture
def test_todo():
    # Crea un'istanza dell'oggetto Todo (il "biscotto" basato sullo stampo della classe)
    todo = Todos(
        title="imparo fast",
        description="ogni giorno",
        priority=5, 
        complete=False,
        owner_id=1,
    )

    # Apre una sessione sul database di test
    db = TestingSessionLocal()
    # Aggiunge l'oggetto todo appena creato alla sessione
    db.add(todo)
    # Salva (commit) le modifiche nel database di test
    db.commit()
    
    # Restituisce l'oggetto 'todo' al test che ha chiamato questa fixture
    yield todo
    
    # --- FASE DI TEARDOWN (Pulizia) ---
    # Questa parte viene eseguita DOPO che il test ha finito il suo lavoro
    with engine.connect() as connection:
        # Esegue una query SQL per eliminare tutti i record dalla tabella 'todos'
        # Questo assicura che il test successivo non trovi dati residui ("spazzatura")
        connection.execute(text("DELETE FROM todos;"))
        # Conferma l'eliminazione
        connection.commit()