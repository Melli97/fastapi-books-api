from routers.todos import get_db,get_current_user
from fastapi import status
from models import Todos
from .utils import *


# Sovrascrive le dipendenze originali con quelle definite sopra
app.dependency_overrides[get_db] = ovveride_get_db
app.dependency_overrides[get_current_user] = override_get_current_user



# ==========================================
# FUNZIONI DI TEST
# ==========================================

# TITOLO: Test lettura di tutti i Todo autenticati
def test_read_all_authenticated(test_todo):
    # Esegue una richiesta GET all'endpoint principale
    response = client.get("/todos")
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
    response = client.get("/todos/todo/1")
    
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
    response = client.get("/todos/todo/999")
    
    # Verifica che il server risponda correttamente con un codice 404 (Not Found)
    assert response.status_code == 404
    
    # Verifica che l'API restituisca il messaggio di errore personalizzato che hai definito nella rotta
    assert response.json() == {'detail': 'todo non trovato'}


# TITOLO: Test creazione di un nuovo Todo (POST)
def test_create_todo(test_todo):
    # Dati che inviamo come payload della richiesta (simuliamo il body di una chiamata POST)
    request_data = {
        'title': 'New todo!',
        'description': 'new todo descrizione',
        'priority': 5,
        'complete': False
    }

    # Esegue la chiamata POST all'endpoint di creazione
    # Il TestClient invia i dati come JSON, esattamente come farebbe un frontend o Postman
    response = client.post('/todos/todo/', json=request_data)
    
    # Verifica che il server abbia risposto con codice 201 (Created), standard per le nuove risorse
    assert response.status_code == 201    

    # --- VERIFICA SUL DATABASE ---
    # Apriamo una sessione sul DB di test per controllare se il record è stato salvato fisicamente
    db = TestingSessionLocal()
    
    # Cerchiamo nel DB il record con ID 2 
    # (assumiamo ID 2 perché la fixture 'test_todo' ha già inserito il record con ID 1)
    model = db.query(Todos).filter(Todos.id == 2).first()
    
    # Asserzioni: confrontiamo i dati salvati nel DB con quelli che abbiamo inviato
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


# ==========================================
# FUNZIONI DI TEST PER UPDATE E DELETE
# ==========================================

# TITOLO: Test aggiornamento di un Todo esistente (PUT)
def test_update_todo(test_todo):
    # Dati inviati per l'aggiornamento
    request_data = {
        'title': 'cambio todo',
        'description': 'ogni giorno',
        'priority': 5, 
        'complete': False,
    }

    # Esegue una richiesta PUT sull'ID 1 (esistente grazie alla fixture)
    response = client.put('/todos/todo/1', json=request_data)
    # Verifica che il server risponda con 204 (No Content), tipico di un aggiornamento riuscito
    assert response.status_code == 204  
    
    # Verifica direttamente nel DB che il record sia stato effettivamente aggiornato
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == 'cambio todo'

# TITOLO: Test aggiornamento di un Todo inesistente (404)
def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'cambio todo',
        'description': 'ogni giorno',
        'priority': 5, 
        'complete': False,
    }

    # Prova ad aggiornare un ID che non esiste nel DB
    response = client.put('/todos/todo/999', json=request_data)
    # Verifica che riceva un errore 404
    assert response.status_code == 404
    # Verifica che il messaggio di errore sia quello corretto (con la 'T' maiuscola)
    assert response.json() == {'detail': 'Todo non trovato'}

# TITOLO: Test cancellazione di un Todo esistente (DELETE)
def test_delete_todo(test_todo):
    # Esegue una richiesta DELETE sull'ID 1
    response = client.delete('/todos/todo/1')
    # Verifica che il server risponda con 204 (No Content)
    assert response.status_code == 204  
    
    # Verifica nel DB che il record non esista più
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    # L'asserzione controlla che la query restituisca None
    assert model is None

# TITOLO: Test cancellazione di un Todo inesistente (404)
def test_delete_todo_not_found(test_todo):
    # Prova a cancellare un ID che non esiste
    response = client.delete('/todos/todo/999')
    # Verifica che riceva un errore 404
    assert response.status_code == 404
    # Verifica il messaggio di errore
    assert response.json() == {'detail': 'Todo non trovato'}