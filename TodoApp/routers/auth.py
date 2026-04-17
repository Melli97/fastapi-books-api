# ===== IMPORT =====
from datetime import datetime, timedelta, timezone
from typing import Annotated
from sqlalchemy.orm import Session  # Importa la classe Session da SQLAlchemy per gestire le sessioni del database
from fastapi import FastAPI, APIRouter,Depends, HTTPException # Importa FastAPI APIRouter per creare gruppi di endpoint
from pydantic import BaseModel
from database import  SessionLocal  # Importa l'engine del database e la classe di sessione locale
from models import Users
from passlib.context import CryptContext #importare per criptare
from starlette import status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm #controlla token
from jose import jwt,JWTError



# ===== ROUTER =====
router = APIRouter(
    prefix ='/auth',
    tags = ['auth']
) # Crea un router: serve per organizzare gli endpoint in moduli separati

# ===== SICUREZZA =====
SECRET_KEY = '72501f8337b492fae4d8130de00ff9676acf4ac880a87d60c288b9db50c6f41d'# Chiave segreta e algoritmo per firmare i JWT
ALGORITHM =  'HS256'

# ===== HASH PASSWORD =====
bcypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')# Configura bcrypt per hashare le password

# ===== TOKEN HANDLER =====
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token') # Prende automaticamente il token dalle richieste


# ===== MODELLI =====
class CreateUserRequest(BaseModel):
    username : str
    email: str
    first_name : str
    last_name : str
    password : str
    role : str
    phone_number: str

class Token(BaseModel): # Modello di risposta del login
    access_token: str
    token_type: str


# ===== DATABASE =====
# Funzione per ottenere una sessione del database
def get_db():
    db = SessionLocal()  # Crea una nuova sessione del database
    try:
        yield db  # Restituisce la sessione per l'uso
    finally:
        db.close()  # Assicura che la sessione venga chiusa al termine dell'uso

# Annotazione per la dipendenza del database
db_dependency = Annotated[Session, Depends(get_db)]

# ===== AUTENTICAZIONE =====
#FUNZIONE AUTENTICAZIONE UTENTE VERIFICA SE PASSWORD E USERNAME CORRETTI
def authenticate_user(username: str, password: str, db):
    # Cerca nel database un utente con lo username fornito
    user = db.query(Users).filter(Users.username == username).first()

    # Se l'utente non esiste, ritorna False (autenticazione fallita)
    if not user:
        return False

    # Verifica la password:
    # confronta la password inserita con quella salvata (hashata) nel database
    if not bcypt_context.verify(password, user.hashed_password):
        return False  # Password errata

    # Se tutto è corretto (utente esiste + password giusta)
    return user


# ===== CREAZIONE TOKEN =====
def create_access_token(username: str, user_id: int,role: str, expires_delta: timedelta):
    # Payload del token
    encode = {
        'sub': username,  # subject (utente)
        'id': user_id,     # id utente
        'role': role
    }

    # Calcola scadenza
    expires = datetime.now(timezone.utc) + expires_delta

    # Aggiunge scadenza al payload
    encode.update({'exp': expires})

    # Crea JWT firmato
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# ===== DECODE TOKEN =====
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    # Questa funzione serve per ottenere l'utente corrente dal token JWT
    # 'token' viene preso automaticamente dalla richiesta (header Authorization: Bearer ...)

    try:
        # Decodifica il token JWT usando la chiave segreta e l'algoritmo
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Estrae lo username dal payload (campo 'sub')
        username: str = payload.get('sub')

        # Estrae l'id utente dal payload
        user_id: int = payload.get('id')

         # Estrae l'ruolo utente dal payload
        user_role: str = payload.get('role')

        # Se uno dei due è None → token non valido
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user non valido"
            )

        # Se tutto è corretto  ritorna i dati dell'utente
        return {'username': username, 'id': user_id , 'role': user_role}

    except JWTError:
        # Se il token è: scaduto- modificato- non valido
        # allora solleva errore 401 (non autorizzato)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user non valido"
        )



# ===== REGISTRAZIONE =====
@router.post("/", status_code= status.HTTP_201_CREATED)
# Definisce un endpoint GET sul percorso /auth/
# Questo endpoint sarà accessibile quando il router viene incluso nell'app principale
async def create_user(db: db_dependency ,
                      create_user_request: CreateUserRequest):
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name =create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = bcypt_context.hash(create_user_request.password), #per criptare passsword
        is_active = True,
        phone_number = create_user_request.phone_number
    )
    db.add(create_user_model)
    db.commit()


# ===== LOGIN =====
@router.post("/token", response_model=Token)
# Serve per effettuare il login e ottenere una risposta (di solito un token)

async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],  
    # OAuth2PasswordRequestForm prende automaticamente:
    # - username
    # - password
    # da una richiesta form (tipica del login)

    db: db_dependency
    # Dipendenza del database: permette di usare la sessione DB
):

    # Chiama la funzione di autenticazione
    # Controlla se username e password sono corretti
    user = authenticate_user(form_data.username, form_data.password, db)

    # Se l'autenticazione fallisce (utente non esiste o password errata)
    if not user:
          raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user non valido"
            )
    
       # Crea token valido 20 minuti
    token = create_access_token(user.username,user.id, user.role,timedelta(minutes=20))
   
    return {'access_token': token, 'token_type': 'bearer' }
 # Se l'autenticazione va a buon fine ritorna token
    # In un'app reale qui si restituisce un TOKEN JWT




#per cryptare password scaricare dipendenze pip install passlib e scaricare dipendenza pip install bcrypt==4.0.1 pip install python-multipart