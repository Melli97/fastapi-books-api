from fastapi import FastAPI, APIRouter
# Importa FastAPI APIRouter per creare gruppi di endpoint

router = APIRouter()
# Crea un router: serve per organizzare gli endpoint in moduli separati

@router.get("/auth/")
# Definisce un endpoint GET sul percorso /auth/
# Questo endpoint sarà accessibile quando il router viene incluso nell'app principale

async def get_user():

    return {'user': 'authenticated'}
    # Restituisce una risposta JSON con un utente "autenticato" 