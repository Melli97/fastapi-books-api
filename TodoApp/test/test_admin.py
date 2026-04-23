from .utils import *
from routers.admin import get_db, get_current_user
from fastapi import status
from models import Todos

# ==========================================
# CONFIGURAZIONE OVERRIDE (MOCKING)
# ==========================================
# Sovrascriviamo le dipendenze originali con quelle di test (DB finto e Admin finto)
app.dependency_overrides[get_db] = ovveride_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# ==========================================
# TEST: LETTURA DATI ADMIN
# ==========================================

def test_admin_read_all_authenticated(test_todo):
    # Esegue la chiamata GET all'endpoint protetto per admin
    response = client.get("/admin/todo")
    
    # Verifica che l'accesso sia consentito (200 OK)
    assert response.status_code == status.HTTP_200_OK
    
    # Verifica che i dati restituiti corrispondano a quelli inseriti dalla fixture
    assert response.json() == [{
        'complete': False, 
        'title': 'imparo fast',
        'description': 'ogni giorno',
        'id': 1, 
        'priority': 5, 
        'owner_id': 1
    }]
    

# ==========================================
# TEST: ELIMINAZIONE TODO
# ==========================================

def test_admin_delete_todo(test_todo):
    # Esegue la chiamata DELETE all'endpoint admin per eliminare l'ID 1
    response = client.delete("/admin/todo/1")    
    
    # Verifica che la cancellazione sia avvenuta con successo (204 No Content)
    assert response.status_code == 204

    # --- VERIFICA SUL DATABASE ---
    # Apriamo una sessione sul DB di test per controllare l'avvenuta eliminazione
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    
    # L'asserzione controlla che il record sia effettivamente sparito (None)
    assert model is None


# ==========================================
# TEST: ELIMINAZIONE TODO INESISTENTE
# ==========================================

def test_admin_delete_todo_not_found(test_todo):
    # Prova a cancellare un ID che non esiste (999)
    response = client.delete('/admin/todo/999') 
    
    # Verifica che il server risponda 404 (Not Found)
    assert response.status_code == 404
    
    # Verifica il messaggio di errore restituito dall'API
    assert response.json() == {'detail': 'todo non trovato'}