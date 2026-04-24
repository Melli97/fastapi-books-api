from .utils import *
from routers.auth import get_db, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM, get_current_user
from jose import jwt
from datetime import timedelta
import pytest
from fastapi import HTTPException

# Sovrascriviamo la dipendenza del database per usare il DB di test
app.dependency_overrides[get_db] = ovveride_get_db

# ==========================================
# TEST: AUTENTICAZIONE UTENTE
# ==========================================
def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    # Caso 1: Autenticazione con credenziali corrette
    authenticated_user = authenticate_user(test_user.username, 'testpassword', db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    # Caso 2: Autenticazione con username inesistente
    non_existent_user = authenticate_user('WrognUsername', 'testpassword', db)
    assert non_existent_user is False

    # Caso 3: Autenticazione con password errata
    wrong_password_user = authenticate_user(test_user.username, 'wrongpassword', db)
    assert wrong_password_user is False

# ==========================================
# TEST: CREAZIONE TOKEN DI ACCESSO
# ==========================================
def test_create_access_token():
    username = 'testuser'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)

    # Genera il token
    token = create_access_token(username, user_id, role, expires_delta)

    # Decodifica il token senza verificare la firma (per testare il contenuto)
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],
                               options={'verify_signature': False})
    
    # Verifica che i dati contenuti nel payload siano corretti
    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role 

# ==========================================
# TEST: VALIDAZIONE TOKEN (GET_CURRENT_USER)
# ==========================================
@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    # Crea un payload e genera un token valido
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    # Verifica che la funzione estragga correttamente i dati dal token
    user = await get_current_user(token=token)
    assert user == {'username': 'testuser', 'id': 1, 'role': 'admin'}

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    # Crea un token che manca delle informazioni necessarie (sub/id)
    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    # Verifica che la funzione sollevi un'eccezione HTTP 401 se il token è incompleto
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'user non valido'

    #pip install pytest-asyncio per gestire funzioni async