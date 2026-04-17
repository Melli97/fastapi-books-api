from database import Base
from sqlalchemy import Column, Integer , String , Boolean ,ForeignKey


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key= True , index= True)    # index=True → migliora la velocità di ricerca
    email = Column(String, unique= True)
    username = Column(String, unique= True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)

# Definizione della classe Todos che rappresenta una tabella nel database
class Todos(Base):

    # Nome della tabella nel database
    __tablename__ = 'todos'

    id = Column(Integer, primary_key= True , index= True)    # index=True → migliora la velocità di ricerca
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column( Integer, ForeignKey("users.id"))