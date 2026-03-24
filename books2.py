from typing import Optional

from fastapi import  FastAPI
from pydantic import BaseModel, Field
app = FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    rating : int


    def __init__(self, id, title, author, description, rating):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating

class BookRequest(BaseModel):
                            #descrivi su http://127.0.0.1:8000/docs 
    id: Optional[int] = Field(description='Id non è necessario crearlo', default=None)  #id opzionale non obbligatori  non passiamo nulla lo passeremo dopo con la funzione
    title: str = Field(min_lenght=3)
    author: str =  Field(min_lenght=3)
    description: str = Field(min_lenght=3, max_length=100)
    rating : int = Field(gt=1,lt =6)

    #Esempio di modello su http://127.0.0.1:8000/docs
    model_config = {
        "json_schema_extra":{
            "example":{
                "title" : "new book",
                "author" : "autore1",
                "description": "descrizione",
                "rating" : 4
            }
        }
    }


BOOKS = [
    Book(1, "Harry Potter", "J.K. Rowling", "Wizard story", 3),
    Book(2, "Il Signore degli Anelli", "Tolkien", "Epic fantasy", 5),
    Book(3, "1984", "George Orwell", "Dystopian future", 5),
    Book(4, "Il Piccolo Principe", "Antoine de Saint-Exupéry", "Philosophical tale", 5),
    Book(5, "Clean Code", "Robert C. Martin", "Programming best practices", 2),
    Book(6, "Clean Code", "Robert C. Martin", "Programming best practices", 1)
]

@app.get("/books") #legge tutti i libri
async def read_all_books():
    return BOOKS


@app.get("/books/{book_id}")        #ricerca tramite id
async def read_book(book_id : int):
    for book in BOOKS:
       if book.id == book_id:
            return book

@app.get("/books/")  
# ATTENZIONE: così com'è, il parametro book_rating sarà una query parameter (es: /books/?book_rating=5)

async def read_book_by_rating(book_rating: int):  
    # Funzione che riceve un rating (numero intero) dalla richiesta
    # FastAPI lo prende dalla query string e lo valida automaticamente

    books_retun = []  
    for book in BOOKS:  
        if book.rating == book_rating:  
           books_retun.append(book)  
    return books_retun  
        


@app.post("/books/create_book")  # Definisce un endpoint POST per creare un libro
async def create_book(book_request: BookRequest):  # Riceve i dati del libro validati da Pydantic
    new_book = Book(**book_request.model_dump())  # ** lasterisco davanti ci permette di assegnare questi argomenti al nuovo libro
    # Converte il modello Pydantic in dizionario e lo usa per creare un oggetto Book
    
    BOOKS.append(find_book_id(new_book))  
    # Aggiunge il nuovo libro alla lista in memoria
     
              
def find_book_id(book: Book):  
    # Funzione che assegna un ID univoco a un libro

    if len(BOOKS) > 0:  
        # Controlla se la lista BOOKS contiene già elementi

        book.id = BOOKS[-1].id + 1  
        # Prende l'ultimo libro della lista (BOOKS[-1])
        # Legge il suo id e aggiunge 1 → così crea un nuovo id progressivo

    else:
        book.id = 1  
        # Se la lista è vuota, assegna il primo id = 1

    return book  
    # Restituisce il libro con l'id aggiornato



@app.post("/books/update_book")  
# Definisce un endpoint POST su /books/update_book
# Serve per aggiornare un libro esistente

async def update_book(book: BookRequest):  
    # Riceve i dati del libro da aggiornare come oggetto Pydantic (BookRequest)
    # FastAPI valida automaticamente che i campi siano corretti

    for i in range(len(BOOKS)):  
        if BOOKS[i].id == book.id:  
            # Controlla se l'id del libro corrente corrisponde all'id del libro da aggiornare

            BOOKS[i] = book  
            # sostituisce l'oggetto esistente con il nuovo oggetto ricevuto



@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
        for i in range(len(BOOKS)):  
            if BOOKS[i].id == book_id:  
                BOOKS.pop(i)
                break