from sqlalchemy import  create_engine, text
from sqlalchemy.pool import StaticPool
from database import Base
from main import app
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import pytest
from models import Todos,Users
from routers.auth import bcypt_context



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
# FIXTURE PER LA GESTIONE DATI TODO
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

# ==========================================
# FIXTURE PER LA GESTIONE DATI UTENTI TEST
# ==========================================

@pytest.fixture
def test_user():
    """
    Fixture per creare un utente di test nel database prima di ogni test
    che richiede un utente autenticato.
    """
    # 1. ISTANZIAZIONE DELL'OGGETTO
    # Creiamo un'istanza del modello SQLAlchemy 'Users'.
    # È come creare un "biscotto" usando lo stampo della classe.
    user = Users(
        username = "Mancio997",
        email = "marcello@gmail.com",
        first_name = "Marcello",
        last_name = "Melli",
        hashed_password = bcypt_context.hash("testpassword"), # La password viene hashata per sicurezza
        role = "admin",
        phone_number = "1111111111"
    )

    # 2. INSERIMENTO NEL DATABASE
    # Apriamo una sessione temporanea di test, aggiungiamo l'utente e salviamo (commit).
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    
    # 3. CONSEGNA DELL'OGGETTO AL TEST
    # 'yield' sospende la funzione e restituisce l'utente appena creato al test.
    # Tutto ciò che segue il 'yield' verrà eseguito DOPO che il test ha concluso il lavoro.
    yield user
    
    # 4. FASE DI TEARDOWN (PULIZIA)
    # È CRUCIALE per garantire l'isolamento dei test. Senza questa fase, i dati
    # dell'utente rimarrebbero nel database, causando errori nei test successivi.
    with engine.connect() as connection:
        # Eseguiamo una query SQL pura per eliminare i dati creati.
        # NOTA: Se hai vincoli di chiavi esterne (foreign keys), assicurati di 
        # eliminare prima le tabelle figlie (es. 'todos') e poi 'users'.
        connection.execute(text("DELETE FROM users;"))
        
        # Confermiamo l'operazione di eliminazione (commit)
        connection.commit()