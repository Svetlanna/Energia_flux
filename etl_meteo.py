import os
import csv

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

FICHIER_ENTREE = "data/meteo-unifie.csv"


def connecter_db():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        port=os.environ["DB_PORT"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )


def charger_lignes_csv(fichier_entree):
    with open(fichier_entree, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def inserer_meteo(connexion, lignes):
    curseur = connexion.cursor()
    requete = """
        INSERT IGNORE INTO meteo (date_heure, temperature, humidite)
        VALUES (%s, %s, %s)
    """
    nb_inserees = 0
    for ligne in lignes:
        curseur.execute(requete, (
            ligne["date_heure"],
            ligne["temperature"] or None,
            ligne["humidite"] or None,
        ))
        if curseur.rowcount == 1:
            nb_inserees += 1
    connexion.commit()
    curseur.close()
    return nb_inserees


if __name__ == "__main__":
    print("Chargement de la meteo dans MySQL...")
    lignes = charger_lignes_csv(FICHIER_ENTREE)
    connexion = connecter_db()
    nb = inserer_meteo(connexion, lignes)
    connexion.close()
    print(f"  {nb} ligne(s) inseree(s)")