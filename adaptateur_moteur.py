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


def recuperer_region(connexion, region_id):
    curseur = connexion.cursor(dictionary=True)
    curseur.execute("SELECT * FROM region WHERE id = %s", (region_id,))
    region = curseur.fetchone()
    curseur.close()
    return region


def calculer_additional_demand_mw(consommation_predite_mw, region):
    reference_mw = region["consommation_moyenne_mw_2024"]
    return max(0.0, consommation_predite_mw - reference_mw)


def construire_requete_moteur(region_id, additional_demand_mw):
    return {
        "region_id": region_id,
        "additional_demand_mw": round(additional_demand_mw, 1),
    }


def charger_scenarios_exemple(fichier_json):
    with open(fichier_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["example_scenarios"]


if __name__ == "__main__":
    connexion = connecter_db()


    region_id = "occitanie"
    consommation_predite_mw = 5000

    region = recuperer_region(connexion, region_id)
    additional_demand_mw = calculer_additional_demand_mw(consommation_predite_mw, region)
    requete = construire_requete_moteur(region_id, additional_demand_mw)

    print("Notre requete construite :")
    print(requete)

    print("\nScenario du prof pour comparaison :")
    for scenario in charger_scenarios_exemple(FICHIER_JSON):
        if scenario["region_id"] == region_id:
            print(scenario)

    connexion.close()