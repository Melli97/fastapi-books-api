
# Importa la funzione per creare la connessione al database
from sqlalchemy import create_engine

# Importa sessionmaker per creare sessioni di lavoro con il DB
from sqlalchemy.orm import sessionmaker 

# Importa la base per creare i modelli (tabelle)
from sqlalchemy.ext.declarative import declarative_base


# URL del database (in questo caso SQLite)
# ./todos.db significa che il file verrà creato nella cartella del progetto
SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'                                     #'postgresql://postgres:marcello97!@localhost/TodoApplicationDatabase'    #collega postgres a fastapi
                            # serve per database sqllite
  
                           

# Crea il motore (engine) che gestisce la connessione al database
# check_same_thread=False serve per evitare errori con SQLite e FastAPI (multi-thread)
engine = create_engine(SQLALCHEMY_DATABASE_URL ,connect_args={'check_same_thread': False})   #, serve per collegare fastapi a datbase sqlite




# Crea una "fabbrica di sessioni"
# autocommit=False → devi salvare manualmente con commit()
# autoflush=False → non invia automaticamente le modifiche al DB
# bind=engine → collega la sessione al database
SessionLocal = sessionmaker(autocommit = False, autoflush= False, bind= engine)


# Base è la classe da cui erediteranno tutti i modelli (tabelle)
# Serve per dire a SQLAlchemy: "queste classi rappresentano tabelle nel DB"
Base = declarative_base()



