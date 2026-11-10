# Guida passo-passo — Come è stata costruita la suite di test (pytest)

Questa guida ripercorre **in ordine logico** tutti i passaggi fatti per arrivare alla suite di test completa, spiegando perché ogni passaggio era necessario prima di passare al successivo.

---

## Passo 1 — Decidere un database separato per i test

**Problema di partenza:** l'app in produzione usa un database vero. Se i test lo usassero, rischieresti di sporcare/cancellare dati reali, e i risultati dei test dipenderebbero da cosa c'è già nel DB (test non ripetibili).

**Soluzione:**

```python
SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
```

- Un secondo motore SQLAlchemy, separato da quello reale, che punta a un file SQLite (`testdb.db`) dedicato solo ai test.
- `check_same_thread: False` e `StaticPool`: necessari perché SQLite di default non permette che la stessa connessione venga usata da thread diversi, mentre FastAPI/TestClient possono gestire le richieste su thread differenti. `StaticPool` forza l'uso di **una singola connessione condivisa** per tutta la sessione di test.
- `Base.metadata.create_all(bind=engine)`: crea fisicamente le tabelle (`users`, `todos`) nel DB di test, usando lo stesso schema (gli stessi modelli SQLAlchemy) dell'app reale.

Questo è il primo mattone: senza un DB isolato, nessun test successivo potrebbe girare in modo sicuro e ripetibile.

---

## Passo 2 — Sostituire le dipendenze reali con quelle finte (Dependency Override)

**Problema:** gli endpoint FastAPI dipendono da `get_db()` (per ottenere la sessione al database) e da `get_current_user()` (per sapere chi è loggato). In produzione, `get_current_user` richiede un vero token JWT ottenuto con login. Fare un login reale ad ogni test sarebbe lento e complicato.

**Soluzione — due funzioni "sostitute":**

```python
def ovveride_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username': 'Mancio997', 'id': 1, 'role': 'admin'}
```

E poi, in ogni file di test che ne ha bisogno:

```python
app.dependency_overrides[get_db] = ovveride_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
```

Da questo momento, ogni volta che un endpoint chiede (tramite `Depends(...)`) il database o l'utente corrente, FastAPI gli dà **queste versioni finte** al posto di quelle reali. Questo è possibile perché l'app è già progettata con **Dependency Injection** — è la stessa architettura descritta nel capitolo di progettazione, ora sfruttata anche per isolare i test.

---

## Passo 3 — Creare un client HTTP finto (`TestClient`)

```python
client = TestClient(app)
```

Per testare gli endpoint servono richieste HTTP vere e proprie (GET, POST, PUT, DELETE). `TestClient` di FastAPI permette di farle **senza avviare un server reale**: le richieste passano comunque attraverso tutto lo stack dell'applicazione (routing → validazione → logica → database), ma tutto avviene "in memoria", in modo veloce.

Con i Passi 1–3 completati, hai un ambiente di test pronto: DB isolato, dipendenze finte, client per le chiamate. Da qui in poi si tratta di popolare i dati e scrivere i test veri.

---

## Passo 4 — Creare le fixture per avere dati pronti prima di ogni test

**Problema:** molti test hanno bisogno che nel DB esista già un Todo o un Utente prima di partire (es. per testare una GET o una modifica).

**Soluzione — fixture con setup e teardown:**

```python
@pytest.fixture
def test_todo():
    todo = Todos(title="imparo fast", description="ogni giorno",
                 priority=5, complete=False, owner_id=1)
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()

    yield todo   # <- il test gira qui, con il todo già presente nel DB

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()
```

Stessa logica per `test_user`, con la differenza che la password viene salvata già **hashata** (`bcypt_context.hash(...)`), esattamente come farebbe l'app reale in fase di registrazione.

Il flusso è:
1. Prima del test → viene creato il dato nel DB (setup)
2. `yield` → il controllo passa al test, che può usare il dato
3. Dopo il test → tutto quello scritto dopo `yield` viene eseguito (teardown), qui una `DELETE` che ripulisce la tabella

Questo garantisce **isolamento**: ogni test parte da uno stato pulito e prevedibile, senza dipendere dall'ordine di esecuzione degli altri test.

---

## Passo 5 — Scrivere i test CRUD sui Todo (`test_todos.py`)

Con l'ambiente pronto, il passo successivo è testare il ciclo di vita completo di un Todo, endpoint per endpoint:

1. **Lettura di tutti i Todo** (`GET /todos`) → verifica status 200 e contenuto della lista
2. **Lettura di un singolo Todo** (`GET /todos/todo/1`) → status 200 e dati corretti
3. **Lettura di un Todo inesistente** (`GET /todos/todo/999`) → status 404 e messaggio d'errore
4. **Creazione** (`POST /todos/todo/`) → status 201, poi verifica **diretta nel database** che il record sia stato salvato davvero
5. **Aggiornamento** (`PUT /todos/todo/1`) → status 204, poi verifica nel DB che il campo sia cambiato
6. **Aggiornamento di un ID inesistente** → status 404
7. **Cancellazione** (`DELETE /todos/todo/1`) → status 204, poi verifica che il record non esista più nel DB
8. **Cancellazione di un ID inesistente** → status 404

Pattern da notare: per le operazioni di scrittura (POST/PUT/DELETE) non ci si accontenta dello status code HTTP, ma si riapre una sessione sul DB e si controlla che il dato sia davvero stato salvato/modificato/eliminato. È una verifica "a doppio livello": comportamento dell'API **e** persistenza reale dei dati.

---

## Passo 6 — Estendere i test al profilo utente (`test_users.py`)

Stessa logica del Passo 5, applicata all'endpoint `/users`:

1. **Lettura profilo** (`GET /users/`) → verifica che tutti i campi (username, email, nome, ruolo, telefono) corrispondano all'utente creato dalla fixture
2. **Cambio password riuscito** → password vecchia corretta, nuova password → status 204
3. **Cambio password fallito** → password vecchia sbagliata → status 401 e messaggio d'errore specifico
4. **Cambio numero di telefono** → aggiornamento tramite **path parameter** invece che body JSON

Qui il passo in più rispetto ai Todo è testare **sia il caso positivo che quello negativo** per un'operazione sensibile come il cambio password: dimostra che l'API rifiuta correttamente le credenziali sbagliate.

---

## Passo 7 — Testare la logica di autenticazione e i token JWT (`test_auth.py`)

Questo è il passaggio più delicato, perché non riguarda solo gli endpoint HTTP ma anche funzioni interne di sicurezza.

**7a. Test diretto della funzione `authenticate_user`**, senza passare da `client.get/post`, ma chiamandola come una normale funzione Python, coprendo 3 casi:
- credenziali corrette → restituisce l'utente
- username inesistente → `False`
- password sbagliata → `False`

**7b. Test della generazione del token** (`create_access_token`): si genera un token e lo si **decodifica** (senza verificare la firma) per controllare che contenga i campi giusti (`sub`, `id`, `role`).

**7c. Test della validazione del token** (`get_current_user`), che è una funzione `async`:

```python
@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    ...
    user = await get_current_user(token=token)
```

Qui serve il plugin `pytest-asyncio` (installato con `pip install pytest-asyncio`) per permettere a pytest di eseguire test `async`. Si coprono due casi: token valido (funziona) e token con dati mancanti (deve sollevare `HTTPException` con status 401 — verificato con `pytest.raises(HTTPException)`).

---

## Passo 8 — Testare gli endpoint riservati agli admin (`test_admin.py`)

Ultimo passaggio: verificare che il livello di **autorizzazione** funzioni, non solo l'autenticazione. Gli endpoint `/admin/todo` richiedono un utente con ruolo `admin` — motivo per cui `override_get_current_user` (Passo 2) restituisce già un utente con `'role': 'admin'`.

- **Lettura di tutti i Todo come admin** → status 200
- **Cancellazione di un Todo come admin** → status 204, poi verifica nel DB che sia stato eliminato
- **Cancellazione di un Todo inesistente** → status 404

Stessa struttura del Passo 5, ma applicata a un endpoint con permessi più ristretti.

---

## Passo 9 — Eseguire tutta la suite

Una volta scritti tutti i test, si eseguono da terminale:

```bash
pytest -v                     # tutti i test, output dettagliato
pytest tests/test_todos.py    # solo un file
pytest -k "password"          # solo i test con "password" nel nome
```

---

## Riepilogo del percorso

| Passo | Obiettivo | Concetto chiave |
|---|---|---|
| 1 | DB isolato | Ambiente di test separato dalla produzione |
| 2 | Override dipendenze | Dependency Injection applicata al testing |
| 3 | Client finto | Simulare richieste HTTP senza server reale |
| 4 | Fixture | Setup/teardown per isolamento tra test |
| 5 | Test CRUD Todo | Verifica HTTP + verifica diretta sul DB |
| 6 | Test profilo utente | Casi positivi e negativi |
| 7 | Test autenticazione/JWT | Test unitari, funzioni async, gestione eccezioni |
| 8 | Test endpoint admin | Verifica autorizzazione (ruoli) |
| 9 | Esecuzione | Comandi pytest |

---

## Da tenere a mente (piccole imprecisioni)

- Refusi nei nomi (`ovveride_get_db`, `bcypt_context`) funzionano ma andrebbero scritti correttamente se citati in tesi.
- `test_create_todo` assume che il nuovo Todo riceva `id == 2`: funziona solo perché SQLite riparte da 1 dopo che il teardown ha svuotato la tabella — è un'assunzione implicita, non una regola generale.
- `from .utils import *` richiede che la cartella dei test sia un package Python (con `__init__.py`).
