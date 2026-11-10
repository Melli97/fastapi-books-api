import os

# Importa la funzione per creare la connessione al database
from sqlalchemy import create_engine

# Importa sessionmaker per creare sessioni di lavoro con il DB
from sqlalchemy.orm import sessionmaker, declarative_base

# URL del database: legge la variabile d'ambiente DATABASE_URL.
# Se non esiste usa SQLite; ./todosapp.db significa che il file
# verrà creato nella cartella del progetto
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todosapp.db")

# check_same_thread=False serve solo per SQLite, per evitare errori
# con FastAPI (multi-thread). Con altri database (es. PostgreSQL) non serve
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

# Crea il motore (engine) che gestisce la connessione al database
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

# Crea una "fabbrica di sessioni"
# autocommit=False → devi salvare manualmente con commit()
# autoflush=False → non invia automaticamente le modifiche al DB
# bind=engine → collega la sessione al database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base è la classe da cui erediteranno tutti i modelli (tabelle)
# Serve per dire a SQLAlchemy: "queste classi rappresentano tabelle nel DB"
Base = declarative_base()