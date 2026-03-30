from fastapi import Body, FastAPI

app = FastAPI()

# Lista di libri
BOOKS = [
    {"title": "Title One", "author": "Author One", "category": "Math"},
    {"title": "Title Two", "author": "Author Two", "category": "Math"},
    {"title": "Title Three", "author": "Author two", "category": "Math"},
    {"title": "Title Four", "author": "Author Four", "category": "Science"},
    {"title": "Title Five", "author": "Author Five", "category": "History"}
]

@app.get("/books") #legge tutti i libri
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
        if book.get('category').lower() == category.lower():
            books_to_return.append(book)
    return books_to_return


@app.get("/books/{book_author}/") #filtraggio per categoria query parameter e autore con path
async def read_category_author_by_query(book_author: str, category: str):
    book_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold() and \
           book.get('category').casefold() == category.casefold():
            book_to_return.append(book)

    return book_to_return


@app.post("/books/create_book")
async def create_book(new_book=Body()): #FastAPI prende il corpo della richiesta HTTP 
    BOOKS.append(new_book)           #(JSON inviato dal client) e lo mette dentro la variabile new_book.
    


@app.put("/books/update_book/") #aggiornare un libro dalla lista
async def update_books(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == updated_book.get('title').casefold():
            BOOKS[i]= updated_book



@app.delete("/books/delete_book/{book_title}") #eliminare un libro dalla lista 
async def delete_book(book_title: str):
        for i in range(len(BOOKS)):
            if BOOKS[i].get('title').casefold() == book_title.casefold():
                BOOKS.pop(i)
               
#l'ordine delle api conta molto endpoint più piccoli sempre in testa al file 
# perchè potrebbero essere consumati da endpoint che accetta piu variabili
@app.get("/books/byauhtor/{author}") #filtraggio per autore con path
async def read_author(author: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == author.casefold():
            books_to_return.append(book)

    return books_to_return