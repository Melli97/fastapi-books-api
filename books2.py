from fastapi import Body, FastAPI

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

@app.post("/books/create_book")
async def create_book(book_request=Body()): #FastAPI prende il corpo della richiesta HTTP 
    BOOKS.append(book_request)           #(JSON inviato dal client) e lo mette dentro la variabile new_book.

