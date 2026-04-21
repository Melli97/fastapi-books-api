from sqlalchemy import  create_engine, text
from sqlalchemy.pool import StaticPool
from database import Base
from main import app
from sqlalchemy.orm import sessionmaker
from routers.todos import get_db,get_current_user
from fastapi.testclient import TestClient
from fastapi import status
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
def override_get_current_user():
    return {'username': 'Mancio997', 'id': 1, 'user_role': 'admin'}

# Sovrascrive le dipendenze originali con quelle definite sopra
app.dependency_overrides[get_db] = ovveride_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

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

# ==========================================
# FUNZIONI DI TEST
# ==========================================

# TITOLO: Test lettura di tutti i Todo autenticati
def test_read_all_authenticated(test_todo):
    # Esegue una richiesta GET all'endpoint principale
    response = client.get("/")
    # Verifica che la chiamata abbia avuto successo (200 OK)
    assert response.status_code == status.HTTP_200_OK
    # Verifica che la risposta sia una lista vuota (perché il DB è appena creato)
    assert response.json() == [{'complete': False , 'title':'imparo fast',
                                'description':'ogni giorno',
                                 'id': 1, 'priority' : 5, 'owner_id': 1}]

# TITOLO: Test lettura di un singolo Todo autenticato
def test_read_one_authenticated(test_todo):
    # Esegue una richiesta GET per leggere uno specifico Todo con ID 1
    # La fixture 'test_todo' garantisce che il record ID 1 sia già presente nel DB
    response = client.get("/todo/1")
    
    # Verifica che la chiamata sia andata a buon fine (200 OK)
    assert response.status_code == status.HTTP_200_OK
    
    # Verifica che il contenuto restituito corrisponda esattamente all'oggetto creato dalla fixture
    assert response.json() == {'complete': False, 'title': 'imparo fast',
                               'description': 'ogni giorno',
                               'id': 1, 'priority': 5, 'owner_id': 1}

# TITOLO: Test lettura di un Todo inesistente (404)
def test_read_one_authenticated_not_found():
    # Esegue una richiesta GET per un ID inesistente (999)
    # Questa volta NON passiamo 'test_todo' perché vogliamo testare l'assenza di dati
    response = client.get("/todo/999")
    
    # Verifica che il server risponda correttamente con un codice 404 (Not Found)
    assert response.status_code == 404
    
    # Verifica che l'API restituisca il messaggio di errore personalizzato che hai definito nella rotta
    assert response.json() == {'detail': 'todo non trovato'}