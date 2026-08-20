import os
import json
from datetime import datetime, timezone

import pandas as pd
import joblib
import mysql.connector
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error


load_dotenv()

DOSSIER_MODELES = "../models"


def connect_db():
     return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        port=os.environ["DB_PORT"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )


def charger_donnees():
    connexion = connect_db()
    requete = """
        SELECT c.date_heure, c.consommation, m.temperature, m.humidite
        FROM consommation c
        LEFT JOIN meteo m
            ON DATE_FORMAT(c.date_heure, '%Y-%m-%d %H:00:00') = m.date_heure
    """
    df = pd.read_sql(requete, connexion)
    connexion.close()

    df["date_heure"] = pd.to_datetime(df["date_heure"], errors="coerce")
    df["consommation"] = pd.to_numeric(df["consommation"], errors="coerce")

    df = df.dropna(subset=["date_heure", "consommation", "temperature", "humidite"])

    return df


def creer_features(df):
    df["heure"] = df["date_heure"].dt.hour
    df["jour_semaine"] = df["date_heure"].dt.dayofweek
    df["mois"] = df["date_heure"].dt.month
    df["weekend"] = (df["jour_semaine"] >= 5).astype(int)
    return df


def sauvegarder_modele(model, mae, features, nb_train, nb_test, dossier_modeles):

    os.makedirs(dossier_modeles, exist_ok=True)

    horodatage = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    nom_modele = f"modele_consommation_{horodatage}"
    chemin_modele = os.path.join(dossier_modeles, f"{nom_modele}.pkl")
    joblib.dump(model, chemin_modele)

    metadata = {
        "nom_modele": nom_modele,
        "date_entrainement": horodatage,
        "algorithme": "RandomForestRegressor",
        "features": features,
        "mae": mae,
        "nb_lignes_entrainement": nb_train,
        "nb_lignes_test": nb_test,
    }
    chemin_metadata = os.path.join(dossier_modeles, f"{nom_modele}.json")
    with open(chemin_metadata, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return chemin_modele, chemin_metadata


def entrainer():

    df = charger_donnees()
    df = creer_features(df)

    features = ["heure", "jour_semaine", "mois", "weekend", "temperature", "humidite"]

    if len(df) < 20:
        raise ValueError(
            f"Seulement {len(df)} ligne(s) apres jointure meteo -- pas assez pour "
            "entrainer. Verifie que la periode couverte par consommation et "
            "meteo se chevauche."
        )

    X = df[features]
    y = df["consommation"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)

    chemin_modele, chemin_metadata = sauvegarder_modele(
        model, mae, features, len(X_train), len(X_test), DOSSIER_MODELES
    )

    return mae, chemin_modele, chemin_metadata


if __name__ == "__main__":
    print("Entrainement du modele de prediction de consommation...")
    mae, chemin_modele, chemin_metadata = entrainer()
    print(f"MAE sur le jeu de test : {mae:.2f} MW")
    print(f"Modele sauvegarde : {chemin_modele}")
    print(f"Metadonnees sauvegardees : {chemin_metadata}")