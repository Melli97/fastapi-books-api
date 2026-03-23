from fastapi import Body, FastAPI
from pydantic import BaseModel
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
    id: int
    title: str
    author: str
    description: str
    rating : int




BOOKS = [
    Book(1, "Harry Potter", "J.K. Rowling", "Wizard story", 3),
    Book(2, "Il Signore degli Anelli", "Tolkien", "Epic fantasy", 5),
    Book(3, "1984", "George Orwell", "Dystopian future", 4),
    Book(4, "Il Piccolo Principe", "Antoine de Saint-Exupéry", "Philosophical tale", 5),
    Book(5, "Clean Code", "Robert C. Martin", "Programming best practices", 2),
    Book(6, "Clean Code", "Robert C. Martin", "Programming best practices", 1)
]

@app.get("/books") #legge tutti i libri
async def read_all_books():
    return BOOKS

@app.post("/books/create_book")  # Definisce un endpoint POST per creare un libro
async def create_book(book_request: BookRequest):  # Riceve i dati del libro validati da Pydantic
    new_book = Book(**book_request.model_dump())  # ** lasterisco davanti ci permette di assegnare questi argomenti al nuovo libro
    # Converte il modello Pydantic in dizionario e lo usa per creare un oggetto Book
    
    BOOKS.append(new_book)  
    # Aggiunge il nuovo libro alla lista in memoria (simula un database)           

