import os
import glob
import json
from datetime import datetime

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DOSSIER_MODELES = "models"


def connecter_db():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        port=os.environ["DB_PORT"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )


def parser_date_entrainement(valeur):
    # format du fichier : "2026-08-19T12-48-54" (tirets a la place des deux-points)
    return datetime.strptime(valeur, "%Y-%m-%dT%H-%M-%S")


def charger_modeles(dossier_modeles=DOSSIER_MODELES):
    fichiers_json = sorted(glob.glob(os.path.join(dossier_modeles, "*.json")))
    if not fichiers_json:
        print(f"Aucun fichier de metadonnees trouve dans {dossier_modeles}")
        return 0

    connexion = connecter_db()
    curseur = connexion.cursor()
    nb_charges = 0

    for chemin in fichiers_json:
        with open(chemin, "r", encoding="utf-8") as f:
            meta = json.load(f)

        nom_fichier = meta["nom_modele"]
        date_entrainement = parser_date_entrainement(meta["date_entrainement"])
        mae = meta.get("mae")
        features_json = json.dumps(meta.get("features", []))

        curseur.execute(
            """
            INSERT INTO modele (nom_fichier, date_entrainement, mae, features_json, actif)
            VALUES (%s, %s, %s, %s, TRUE)
            ON DUPLICATE KEY UPDATE
                date_entrainement = VALUES(date_entrainement),
                mae = VALUES(mae),
                features_json = VALUES(features_json)
            """,
            (nom_fichier, date_entrainement, mae, features_json),
        )
        nb_charges += 1
        print(f"  {nom_fichier} -> mae={mae:.2f}" if mae is not None else f"  {nom_fichier}")

    connexion.commit()
    curseur.close()
    connexion.close()
    return nb_charges


if __name__ == "__main__":
    print("Chargement des metadonnees de modeles dans la table modele...")
    nb = charger_modeles()
    print(f"Termine : {nb} modele(s) traite(s).")