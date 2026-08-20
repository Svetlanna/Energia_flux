import os
from datetime import datetime, timezone, timedelta

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from dotenv import load_dotenv

from prediction import charger_dernier_modele, predire, FEATURES

load_dotenv()

app = FastAPI()


class EntreePrediction(BaseModel):
    heure: int
    jour_semaine: int
    mois: int
    weekend: int
    temperature: float
    humidite: float


try:
    modele, version_modele = charger_dernier_modele("../models")
except FileNotFoundError:
    modele, version_modele = None, None
    print("Aucun modele disponible au demarrage.")


def connecter_db():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        port=os.environ["DB_PORT"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )


def enregistrer_prediction(entree, resultat, version_modele):
    try:
        connexion = connecter_db()
        curseur = connexion.cursor()

        curseur.execute(
            "SELECT id FROM modele WHERE nom_fichier = %s", (version_modele,)
        )
        ligne = curseur.fetchone()
        if ligne is None:
            print(f"Avertissement : modele {version_modele} absent de la table modele.")
            curseur.close()
            connexion.close()
            return

        curseur.execute(
            """
            INSERT INTO prediction
                (date_prediction, heure, jour_semaine, mois, valeur_predite_mw, modele_utilise)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                datetime.now(timezone.utc),
                entree.heure,
                entree.jour_semaine,
                entree.mois,
                resultat,
                ligne[0],
            ),
        )
        connexion.commit()
        curseur.close()
        connexion.close()
    except Exception as erreur:
        print(f"Avertissement : echec de la tracabilite ({erreur}).")


def expliquer_prediction(model, entree):
    importances = model.feature_importances_
    valeurs = entree.dict()

    paires = sorted(zip(FEATURES, importances), key=lambda x: x[1], reverse=True)
    top3 = paires[:3]

    details = ", ".join(
        f"{nom} = {valeurs[nom]} (poids {importance:.0%})"
        for nom, importance in top3
    )
    return f"Les facteurs les plus influents pour ce modele sont : {details}."


CACHE_TTL_SECONDES = 600  # 10 minutes
cache_predictions = {}


def cle_cache(entree: EntreePrediction):
    return (
        entree.heure, entree.jour_semaine, entree.mois,
        entree.weekend, entree.temperature, entree.humidite,
    )


@app.post("/predict")
def predict(entree: EntreePrediction):
    if modele is None:
        raise HTTPException(
            status_code=503,
            detail="Modele indisponible : aucun modele entraine trouve.",
        )

    cle = cle_cache(entree)
    maintenant = datetime.now(timezone.utc)

    if cle in cache_predictions:
        resultat_cache, explication_cache, expiration = cache_predictions[cle]
        if maintenant < expiration:
            return {
                "prediction_mw": round(resultat_cache, 1),
                "model_version": version_modele,
                "timestamp": maintenant.isoformat(),
                "explication": explication_cache,
                "depuis_cache": True,
            }

    resultat = predire(modele, entree.dict())
    explication = expliquer_prediction(modele, entree)
    cache_predictions[cle] = (resultat, explication, maintenant + timedelta(seconds=CACHE_TTL_SECONDES))
    enregistrer_prediction(entree, resultat, version_modele)

    return {
        "prediction_mw": round(resultat, 1),
        "model_version": version_modele,
        "timestamp": maintenant.isoformat(),
        "explication": explication,
        "depuis_cache": False,
    }