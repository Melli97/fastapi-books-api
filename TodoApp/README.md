#  TodoApp - FastAPI Backend

Una moderna applicazione di backend per la gestione di compiti (Todo) personali, dotata di un sistema completo di autenticazione, gestione utenti e permessi amministrativi. Il progetto è sviluppato in Python utilizzando il framework ad alte prestazioni **FastAPI** e **SQLAlchemy** come ORM.

---

##  Architettura del Progetto

Il progetto è strutturato in modo modulare per separare chiaramente le responsabilità:

*   `main.py`: Punto di ingresso dell'applicazione, configurazione di FastAPI e inizializzazione del database.
*   `database.py`: Configurazione della connessione al database SQLite.
*   `models.py`: Definizione delle tabelle del database (`Users` e `Todos`) e delle loro relazioni.
*   `auth.py`: Gestione della sicurezza, hashing delle password e generazione/verifica dei Token JWT.
*   `routers/`:
    *   `todos.py`: Operazioni CRUD per i compiti degli utenti loggati.
    *   `users.py`: Gestione del profilo utente e cambio password.
    *   `admin.py`: Funzionalità di monitoraggio e moderazione riservate agli amministratori.

---

## Funzionalità Principali

1. **Autenticazione Sicura**: Registrazione e Login conformi allo standard OAuth2 con token **JWT (JSON Web Tokens)** con scadenza a 20 minuti. Le password sono protette nel database tramite hashing **Bcrypt**.
2. **Isolamento dei Dati**: Ogni utente può visualizzare, creare, modificare o eliminare esclusivamente i *propri* Todo.
3. **Controllo degli Accessi Basato sui Ruoli (RBAC)**: Gli utenti con ruolo `admin` hanno accesso a endpoint dedicati per visualizzare ed eliminare i compiti di chiunque.
4. **Validazione Rigorosa**: Tutti i dati in ingresso e in uscita sono controllati e validati tramite modelli **Pydantic**.

---

##  Tecnologie Utilizzate

*   **Python 3.x**
*   **FastAPI**: Framework web per API veloci e performanti.
*   **SQLAlchemy**: ORM per la gestione del database tramite oggetti Python.
*   **SQLite**: Database relazionale locale.
*   **Passlib (Bcrypt)**: Per la crittografia delle password.
*   **Python-Jose**: Per la firma e la decodifica dei token JWT.

---

##  Come Avviare il Progetto Localmente

### 1. Clonare il progetto o posizionarsi nella cartella
Apri il terminale nella directory principale del progetto.

### 2. Creare e attivare l'ambiente virtuale
```bash
# Su Windows
python -m venv venv
.\venv\Scripts\activate
source fastapienv/Scripts/activate
# Su macOS/Linux
python3 -m venv venv
source venv/bin/activate

#### 3. Installare le dipendenze 
Installa tutte le librerie incluse nel file `requirements.txt` lanciando:

```bash
pip install -r requirements.txt

#### 4. impostare la GEMINI_API_KEY prima di avviare il server


fai partire il server uvicorn main:app --reload