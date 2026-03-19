from fastapi import FastAPI

app = FastAPI()

# Lista di libri
# List of books in English
BOOKS = [
    {"title": "Title One", "author": "Author One", "category": "Math"},
    {"title": "Title Two", "author": "Author Two", "category": "Math"},
    {"title": "Title Three", "author": "Author two", "category": "Math"},
    {"title": "Title Four", "author": "Author Four", "category": "Science"},
    {"title": "Title Five", "author": "Author Five", "category": "History"}
]

@app.get("/endpoint")
def home():
    return {"messaggio": "Funziona!"}

@app.get("/books")
async def read_all_books():
    return BOOKS

@app.get("/books/{book_title}")
async def read_book(book_title : str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():

            return book
        
@app.get("/books/") #filtraggio per categoria query parameter
async def read_category_by_query(category: str): # FastAPI capisce che è una query perché NON è nel path "/libri/"
    books_to_return = []
    for book in BOOKS:
        if book.get('category', '').lower() == category.lower():
            books_to_return.append(book)
    return books_to_return


@app.get("/books/{book_author}/")
async def read_category_by_query(book_author: str, category: str):
    book_to_return = []

    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold() and \
           book.get('category').casefold() == category.casefold():
            book_to_return.append(book)

    return book_to_return