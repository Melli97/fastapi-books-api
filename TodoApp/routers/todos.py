from typing import Annotated  # Importa Annotated per annotare il tipo di dipendenze
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session  # Importa la classe Session da SQLAlchemy per gestire le sessioni del database
from fastapi import APIRouter, Depends, HTTPException, Path , Request , status # Importa FastAPI per creare l'router e Depends per gestire le dipendenze
from models import Todos  # Importa il modello Todos dal modulo models
from database import  SessionLocal  # Importa l'engine del database e la classe di sessione locale
from starlette import status  # Codici HTTP (es. 200, 302, 401)
from .auth import get_current_user # Verifica identità utente (JWT)
from starlette.responses import RedirectResponse # Reindirizzamento del browser
from fastapi.templating import Jinja2Templates   # Motore per pagine HTML (Jinja2)


templates = Jinja2Templates( directory="templates")

# Crea un'istanza dell'app FastAPI
router = APIRouter(
    prefix='/todos',
    tags= ['todos']
)




# Funzione per ottenere una sessione del database
def get_db():
    db = SessionLocal()  # Crea una nuova sessione del database
    try:
        yield db  # Restituisce la sessione per l'uso
    finally:
        db.close()  # Assicura che la sessione venga chiusa al termine dell'uso

# Annotazione per la dipendenza del database
db_dependency = Annotated[Session, Depends(get_db)]

# Definizione di una dependency per ottenere l'utente autenticato
user_dependency = Annotated[dict, Depends(get_current_user)]


 # Definisce uno schema Pydantic
# Serve per validare e strutturare i dati ricevuti dal client (request body)
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length= 100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


def redirect_to_login():
    redirect_response = RedirectResponse(url ="/auth/login-page", status_code= status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response


#### PAGINE DI INTERFACCIA UTENTE (UI) #########


@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    """
    Carica e restituisce il file HTML del modulo di todo.
    """
    try:
        # Tenta di recuperare l'utente corrente leggendo il JWT (access_token) dai cookie della richiesta
        user = await get_current_user(request.cookies.get('access_token'))
        
        # Se il token non è presente o non è valido (get_current_user restituisce None),
        # reindirizza l'utente alla pagina di login
        if user is None:
            return redirect_to_login()
        
        # Interroga il database per ottenere tutti i "todos" che appartengono all'utente loggato
        # Viene filtrato per 'owner_id' usando l'ID estratto dal dizionario/oggetto user
        todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

        # Restituisce la risposta caricando il template Jinja2 "todo.html"
        # Passa al template l'oggetto 'request' (obbligatorio) e la lista dei 'todos' recuperati
        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos})
    
    except:
        # cattura l'eccezione e riporta l'utente in sicurezza alla pagina di login
        return redirect_to_login()
###############################################




#LEGGERE TUTTI I TODO
@router.get("/", status_code= status.HTTP_200_OK)
async def read_all(user: user_dependency,db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Autenticazione fallita')
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()  # Esegue una query per ottenere tutte le voci nella tabella Todos


#RICERCA TODO TRAMITE ID PATH
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)  # Se la richiesta ha successo, restituisce HTTP 200

async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    # db: viene iniettato automaticamente tramite la dependency (sessione DB)
    # todo_id: parametro preso dall'URL
    # Path(gt=0): valida che todo_id sia > 0

    if user is None:
         raise HTTPException(status_code=401, detail='Autenticazione fallita')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    # Query al database:
    # - cerca nella tabella Todos
    # - filtra per id uguale a todo_id
    # - prende il primo risultato trovato (oppure None se non esiste)

    if todo_model is not None:
        return todo_model     # Se il todo esiste, lo restituisce come risposta
   
    raise HTTPException(status_code=404, detail='todo non trovato')
    # Se non esiste nessun record con quell'id:
    # - restituisce errore 404 (Not Found)


#CREAZIONE TODO    
@router.post("/todo", status_code=status.HTTP_201_CREATED)
# Serve per creare una nuova risorsa (todo)

async def create_todo(user:user_dependency, db: db_dependency, todo_request: TodoRequest):
        # user → utente autenticato (preso da get_current_user tramite Depends)
    # db: sessione del database (iniettata automaticamente con Depends)
    # todo_request: dati ricevuti dal body della richiesta (schema Pydantic)


    if user is None:
        raise HTTPException(status_code=401, detail='Autenticazione fallita')

    todo_model = Todos(**todo_request.model_dump(), owner_id = user.get('id')) #owner_id assegna l'id dell'utente come proprietario
    # Converte i dati ricevuti (Pydantic) in un modello SQLAlchemy
    # model_dump() trasforma todo_request in un dizionario
    # ** spacchetta il dizionario nei parametri del costruttore di Todos

    db.add(todo_model)
    # Aggiunge il nuovo oggetto alla sessione del database

    db.commit()
    # Salva definitivamente i cambiamenti nel database (INSERT reale)


#AGGIORNARE TODO PUT
@router.put("/todo/{todo_id}", status_code= status.HTTP_204_NO_CONTENT)

async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest ,todo_id : int= Path(gt=0)):
    # db: sessione database (iniettata automaticamente)
    # todo_request: dati aggiornati inviati dal client (body della richiesta)
    # todo_id: id del todo preso dall'URL
    # Path(gt=0): valida che l'id sia maggiore di 0

    if user is None:
        raise HTTPException(status_code=401, detail='Autenticazione fallita')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    # Cerca nel database il todo con l'id specificato
    # .first() restituisce il primo risultato oppure None se non esiste

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo non trovato")
    #aggiorna campi
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    # Aggiunge il nuovo oggetto alla sessione del database      
    db.commit()
    # Salva le modifiche nel database (UPDATE reale)


#ELIMINARE TODO   
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
# Endpoint DELETE per eliminare un todo

async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    # db: sessione database (iniettata automaticamente)

    if user is None:
        raise HTTPException(status_code=401, detail='Autenticazione fallita')
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    # Cerca il todo nel database

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo non trovato")

    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()
    #db.delete(todo_model)
    # Elimina il record dal database

    db.commit()
    # Conferma la cancellazione (DELETE reale)  


