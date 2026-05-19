import json
from fastapi import APIRouter, HTTPException, status
from google import genai
from google.genai import types
from pydantic import BaseModel
from enum import Enum

# Crea un router FastAPI per organizzare le rotte dell'applicazione.
# Tutte le rotte di questo router avranno il prefisso "/ai" e il tag "AI Assistant" nella documentazione OpenAPI/Swagger.
router = APIRouter(prefix="/ai", tags=["AI Assistant"])

# Inizializza il client ufficiale di Gemini.
# Di default, cerca la variabile d'ambiente GEMINI_API_KEY per l'autenticazione.
client = genai.Client()



# Definiamo una classe Enum (Enumerazione) che eredita anche da 'str' (stringa).
# Questo dice a Python e a FastAPI che i valori accettati sono solo e soltanto questi,
# e che si comportano a tutti gli effetti come normali stringhe di testo.
class TaskCategory(str, Enum):
    SPESA = "Spesa"
    LAVORO = "Lavoro"
    PERSONALE = "Personale"
    SALUTE = "Salute"
    CASA = "Casa"
    ALTRO = "Altro"

# Definisce lo schema dei dati attesi in risposta utilizzando Pydantic.
class CategorizeResponse(BaseModel):
    category: TaskCategory

# Definisce lo schema dei dati attesi in risposta utilizzando Pydantic.
# Questo garantisce la validazione dei dati sia lato Gemini (Structured Outputs) sia lato FastAPI.
class SubTaskResponse(BaseModel):
    subtasks: list[str]

# Definisce un endpoint POST all'indirizzo "/ai/suggest-subtasks".
# Specifica che la risposta corretta seguirà il modello Pydantic SubTaskResponse.
@router.post("/suggest-subtasks", response_model=SubTaskResponse)
async def generate_subtasks(todo_title: str):
    """
    Endpoint che accetta il titolo di un task principale e, tramite l'IA di Gemini,
    lo scompone in un elenco di massimo 4 sotto-compiti in formato JSON strutturato.
    """
    try:
        # Prepara il prompt testuale da inviare al modello, inserendo il task dell'utente.
        prompt = f"Scomponi questo compito in massimo 4 sotto-compiti pratici e brevi: {todo_title}"
        
        # Effettua la chiamata asincrona (o sincrona, a seconda del contesto dell'SDK) al modello Gemini.
        response = client.models.generate_content(
            model='gemini-2.5-flash', # Utilizza il modello Gemini 2.5 Flash, ideale per task veloci e strutturati
            contents=prompt,
            config=types.GenerateContentConfig(
                # Forza il modello a restituire una stringa in formato JSON valido
                response_mime_type="application/json",
                # Passa la classe Pydantic come schema. Gemini adatterà il suo output 
                # esattamente a questa struttura, garantendo la presenza del campo 'subtasks'.
                response_schema=SubTaskResponse,
            ),
        )
        
        # response.text contiene la stringa JSON generata da Gemini (es. '{"subtasks": ["...", "..."]}').
        # json.loads() la trasforma in un dizionario Python. 
        # FastAPI, grazie a `response_model=SubTaskResponse`, lo convaliderà e lo invierà come JSON al client.
        return json.loads(response.text)
        
    except Exception as e:
        # In caso di errori (es. API key mancante, problemi di rete o di validazione),
        # restituisce un errore HTTP 500 (Internal Server Error) con il dettaglio dell'errore.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Errore dell'IA: {str(e)}"
        )
    

# Definisce la rotta POST e assicura che l'output segua lo schema CategorizeResponse
@router.post("/categorize-task", response_model=CategorizeResponse)
async def categorize_task(todo_title: str):
    try:
        # Crea il messaggio unendo l'istruzione al titolo del task dell'utente
        prompt = f"Assegna una sola categoria a questo compito: '{todo_title}'"
        
        # Chiama il modello Gemini configurando la risposta
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", # Chiede un output in formato JSON
                response_schema=CategorizeResponse,    # Obbliga l'IA a usare solo le categorie dell'Enum
                temperature=0.1,                       # Abbassa la fantasia dell'IA per risposte precise e stabili
            ),
        )
        
        # Trasforma la stringa JSON ricevuta da Gemini in un dizionario Python e lo restituisce
        return json.loads(response.text)
        
    except Exception as e:
        # Se qualcosa va storto, risponde con un errore del server 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Errore: {str(e)}"
        )