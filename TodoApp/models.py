from database import Base
from sqlalchemy import Column, Integer , String , Boolean

# Definizione della classe Todos che rappresenta una tabella nel database
class Todos(Base):

    # Nome della tabella nel database
    __tablename__ = 'todos'

    id = Column(Integer, primary_key= True , index= True)    # index=True → migliora la velocità di ricerca
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)