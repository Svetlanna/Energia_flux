import os
import json

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

FICHIER_JSON = "data/parc_nucleaire_prescriptif_france.json"


def connecter_db():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        port=os.environ["DB_PORT"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )


def charger_regions(fichier_json):
    with open(fichier_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["regions"]


def inserer_regions(connexion, regions):
    curseur = connexion.cursor()
    requete = """
        INSERT INTO region
            (id, insee_code, nom, population_2023, consommation_moyenne_mw_2024,
             pic_illustratif_mw, connectee_reseau_continental)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            insee_code = VALUES(insee_code),
            nom = VALUES(nom),
            population_2023 = VALUES(population_2023),
            consommation_moyenne_mw_2024 = VALUES(consommation_moyenne_mw_2024),
            pic_illustratif_mw = VALUES(pic_illustratif_mw),
            connectee_reseau_continental = VALUES(connectee_reseau_continental)
    """
    nb = 0
    for region in regions:
        curseur.execute(requete, (
            region["id"],
            region["insee_code"],
            region["name"],
            region["population_2023"],
            region["average_consumption_mw_2024"],
            region["illustrative_peak_consumption_mw"],
            region["connected_to_continental_grid"],
        ))
        nb += 1
    connexion.commit()
    curseur.close()
    return nb


if __name__ == "__main__":
    print("Chargement des regions dans la table region...")
    regions = charger_regions(FICHIER_JSON)
    connexion = connecter_db()
    nb = inserer_regions(connexion, regions)
    connexion.close()
    print(f"  {nb} region(s) chargee(s)")