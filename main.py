from fastapi import FastAPI

app = FastAPI()

# Lista di libri
# List of books in English
BOOKS = [
    {"title": "Title One", "author": "Author One", "category": "Math"},
    {"title": "Title Two", "author": "Author Two", "category": "Math"},
    {"title": "Title Three", "author": "Author Three", "category": "Math"},
    {"title": "Title Four", "author": "Author Four", "category": "Science"},
    {"title": "Title Five", "author": "Author Five", "category": "History"}
]

@app.get("/endpoint")
def home():
    return {"messaggio": "Funziona!"}

@app.get("/books")
async def read_all_books():
    return BOOKS

@app.get("/libri/{book_title}")
async def read_book(book_title : str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():

            return book