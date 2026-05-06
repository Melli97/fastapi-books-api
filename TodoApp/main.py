from fastapi import FastAPI, Request, status

from fastapi.staticfiles import StaticFiles
import models  # Importa il modulo models, che contiene i modelli del database
from database import engine  # Importa l'engine del database e la classe di sessione locale
from routers import auth, todos, admin, users  # import file auth
from fastapi.responses import RedirectResponse


# ==========================================
# 1. INIZIALIZZAZIONE APP E DATABASE
# ==========================================
# Crea un'istanza dell'app FastAPI
app = FastAPI()

# Crea le tabelle nel database utilizzando i modelli definiti
models.Base.metadata.create_all(bind=engine)


# ==========================================
# 2. CONFIGURAZIONE RISORSE (TEMPLATES E STATIC)
# ==========================================
# 1. Inizializzazione del motore dei template
# Diciamo a FastAPI dove si trovano i file HTML (nella cartella 'templates')
# Jinja2 è il motore che permette di inserire dati dinamici dentro l'HTML
#templates = Jinja2Templates(directory="templates")

# Monta una directory statica per servire file che non cambiano
# - "/static": È il prefisso dell'URL che userai nel browser o nell'HTML.
# - directory="static": È la cartella nel tuo computer dove sono salvati fisicamente i file.
# - name="static": È un identificativo interno per FastAPI (utile per generare URL nei template).
app.mount("/static", StaticFiles(directory="static"), name="static")


# ==========================================
# 3. ROTTE WEB (TEMPLATE RENDERING)
# ==========================================
# 2. Rotta principale (Home Page)
# Il decoratore @app.get("/") indica che questa funzione risponde alle chiamate browser sulla home
@app.get("/")
def test(request: Request):
    # 'request: Request' è un oggetto che contiene le informazioni sulla richiesta HTTP (IP, headers, ecc.)
    # È obbligatorio passarlo a TemplateResponse per permettere a Jinja2 di generare link e URL correttamente.
    
    # TemplateResponse cerca il file 'home.html' nella cartella 'templates' 
    # e lo restituisce al browser, iniettando l'oggetto 'request' nel contesto
    return RedirectResponse(url="/todos/todo-page" , status_code= status.HTTP_302_FOUND)


# ==========================================
# 4. ROTTE DI SISTEMA (API)
# ==========================================
# 3. Rotta di monitoraggio (Health Check)
# Questa rotta serve solitamente per verificare se il server è attivo e funzionante
@app.get("/healthy")
def health_check():
    # Restituisce un dizionario Python; FastAPI lo trasforma automaticamente 
    # in una risposta JSON con stato HTTP 200 (OK)
    return {'status': 'healthy'}


# ==========================================
# 5. REGISTRAZIONE ROUTER (MODULARIZZAZIONE)
# ==========================================
# Aggiunge all'app FastAPI tutti gli endpoint definiti nel router del file auth
# auth.router è un oggetto APIRouter che contiene le rotte (es: login, register)
# In questo modo puoi organizzare il progetto in più file invece di avere tutto in main.py
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)






#################################################################################################
# prima di suddividere

# # Funzione per ottenere una sessione del database
# def get_db():
#     db = SessionLocal()  # Crea una nuova sessione del database
#     try:
#         yield db  # Restituisce la sessione per l'uso
#     finally:
#         db.close()  # Assicura che la sessione venga chiusa al termine dell'uso

# # Annotazione per la dipendenza del database
# db_dependency = Annotated[Session, Depends(get_db)]

#  # Definisce uno schema Pydantic
# # Serve per validare e strutturare i dati ricevuti dal client (request body)
# class TodoRequest(BaseModel):
#     title: str = Field(min_length=3)
#     description: str = Field(min_length=3, max_length= 100)
#     priority: int = Field(gt=0, lt=6)
#     complete: bool


# #LEGGERE TUTTI I TODO
# @app.get("/", status_code= status.HTTP_200_OK)
# async def read_all(db: db_dependency):
#     return db.query(Todos).all()  # Esegue una query per ottenere tutte le voci nella tabella Todos


# #RICERCA TODO TRAMITE ID PATH
# @app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)  # Se la richiesta ha successo, restituisce HTTP 200

# async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
#     # db: viene iniettato automaticamente tramite la dependency (sessione DB)
#     # todo_id: parametro preso dall'URL
#     # Path(gt=0): valida che todo_id sia > 0

#     todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
#     # Query al database:
#     # - cerca nella tabella Todos
#     # - filtra per id uguale a todo_id
#     # - prende il primo risultato trovato (oppure None se non esiste)

#     if todo_model is not None:
#         return todo_model     # Se il todo esiste, lo restituisce come risposta
   
#     raise HTTPException(status_code=404, detail='todo non trovato')
#     # Se non esiste nessun record con quell'id:
#     # - restituisce errore 404 (Not Found)


# #CREAZIONE TODO    
# @app.post("/todo", status_code=status.HTTP_201_CREATED)
# # Serve per creare una nuova risorsa (todo)

# async def create_todo(db: db_dependency, todo_request: TodoRequest):
#     # db: sessione del database (iniettata automaticamente con Depends)
#     # todo_request: dati ricevuti dal body della richiesta (schema Pydantic)

#     todo_model = Todos(**todo_request.model_dump())
#     # Converte i dati ricevuti (Pydantic) in un modello SQLAlchemy
#     # model_dump() trasforma todo_request in un dizionario
#     # ** spacchetta il dizionario nei parametri del costruttore di Todos

#     db.add(todo_model)
#     # Aggiunge il nuovo oggetto alla sessione del database

#     db.commit()
#     # Salva definitivamente i cambiamenti nel database (INSERT reale)


# #AGGIORNARE TODO PUT
# @app.put("/todo/{todo_id}", status_code= status.HTTP_204_NO_CONTENT)

# async def update_todo(db: db_dependency, todo_request: TodoRequest ,todo_id : int= Path(gt=0)):
#     # db: sessione database (iniettata automaticamente)
#     # todo_request: dati aggiornati inviati dal client (body della richiesta)
#     # todo_id: id del todo preso dall'URL
#     # Path(gt=0): valida che l'id sia maggiore di 0

#     todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
#     # Cerca nel database il todo con l'id specificato
#     # .first() restituisce il primo risultato oppure None se non esiste

#     if todo_model is None:
#         raise HTTPException(status_code=404, detail="Todo non trovato")
#     #aggiorna campi
#     todo_model.title = todo_request.title
#     todo_model.description = todo_request.description
#     todo_model.priority = todo_request.priority
#     todo_model.complete = todo_request.complete

#     db.add(todo_model)
#     # Aggiunge il nuovo oggetto alla sessione del database      
#     db.commit()
#     # Salva le modifiche nel database (UPDATE reale)


# #ELIMINARE TODO   
# @app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
# # Endpoint DELETE per eliminare un todo

# async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
#     # db: sessione database (iniettata automaticamente)

#     todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
#     # Cerca il todo nel database

#     if todo_model is None:
#         raise HTTPException(status_code=404, detail="Todo non trovato")

#     db.query(Todos).filter(Todos.id == todo_id).delete()
#     #db.delete(todo_model)
#     # Elimina il record dal database

#     db.commit()
#     # Conferma la cancellazione (DELETE reale)  


