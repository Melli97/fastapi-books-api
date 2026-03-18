from fastapi import FastAPI

app = FastAPI()

libri = {
    "libro1": {
        "titolo": "Il nome della rosa",
        "autore": "Umberto Eco",
        "categoria": "Romanzo storico"
    },
    "libro2": {
        "titolo": "1984",
        "autore": "George Orwell",
        "categoria": "Distopico"
    },
    "libro3": {
        "titolo": "Il Signore degli Anelli",
        "autore": "J.R.R. Tolkien",
        "categoria": "Fantasy"
    }
}

@app.get("/endpoint")
def home():
    return {"messaggio": "Funziona!"}

@app.get("/libri")
async def read_all_books():
    return libri