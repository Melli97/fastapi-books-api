from .utils import *
from routers.users import get_db, get_current_user
from fastapi import status

# --- CONFIGURAZIONE OVERRIDE ---
# Sostituiamo le dipendenze reali (DB e Auth) con quelle di test
# per isolare i test e non interagire con il database di produzione.
app.dependency_overrides[get_db] = ovveride_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# ==============================================================================
# TEST: RECUPERO INFORMAZIONI UTENTE
# ==============================================================================
def test_return_user(test_user):
    # Verifica che il GET /users/ restituisca correttamente i dati dell'utente loggato
    response = client.get("/users/") 
    
    # Conferma che la richiesta sia andata a buon fine (200 OK)
    assert response.status_code == status.HTTP_200_OK
    
    # Verifica che tutti i campi nel JSON corrispondano ai dati dell'utente creato dalla fixture
    assert response.json()['username'] == 'Mancio997'
    assert response.json()['email'] == 'marcello@gmail.com'
    assert response.json()['first_name'] == 'Marcello'
    assert response.json()['last_name'] == 'Melli'
    assert response.json()['role'] == 'admin'
    assert response.json()['phone_number'] == '1111111111'

# ==============================================================================
# TEST: CAMBIO PASSWORD
# ==============================================================================
def test_change_password_success(test_user):
    # Simula una richiesta PUT per cambiare la password fornendo la vecchia corretta
    response = client.put("/users/password", json={
        "password": "testpassword",
        "new_password": "newpassword"
    }) 
    # Un cambio riuscito dovrebbe restituire 204 No Content
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_invalid_current_password(test_user):
    # Simula un tentativo fallito di cambiare password fornendo una password vecchia errata
    response = client.put("/users/password", json={
        "password": "wrongpassword",
        "new_password": "newpassword"
    }) 
    # Verifica che venga restituito l'errore 401 Unauthorized
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # Verifica che il messaggio di errore sia quello previsto
    assert response.json() == {'detail': 'Errore sulla password'}

# ==============================================================================
# TEST: CAMBIO NUMERO DI TELEFONO
# ==============================================================================
def test_change_phone_number_success(test_user):
    # Simula una richiesta PUT per aggiornare il numero di telefono tramite Path Parameter
    response = client.put("/users/phonenumber/2222222222")
    # Verifica che l'aggiornamento sia andato a buon fine (204 No Content)
    assert response.status_code == status.HTTP_204_NO_CONTENT