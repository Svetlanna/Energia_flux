from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from prediction import charger_dernier_modele, predire

app = FastAPI()



class EntreePrediction(BaseModel):

    heure: int
    jour_semaine: int
    mois: int
    nucleaire: float
    eolien: float
    solaire: float
    hydraulique: float
    taux_co2: float


try:
    modele, version_modele = charger_dernier_modele("../models")
except FileNotFoundError:
    # Le service demarre quand meme, mais sans modele charge.
    # On le signale clairement au lieu de laisser planter tout le programme.
    modele, version_modele = None, None
    print("Aucun modele disponible au demarrage.")


@app.post("/predict")
def predict(entree: EntreePrediction):
    if modele is None:
        # HTTPException avec status_code=503 renvoie une vraie erreur HTTP
        # au client, avec un message explicite, plutot qu'un plantage brut.
        raise HTTPException(
            status_code=503,
            detail="Modele indisponible : aucun modele entraine trouve.",
        )

    resultat = predire(modele, entree.dict())

    return {
        "prediction_mw": round(resultat, 1),
        "model_version": version_modele,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }