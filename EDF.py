import os
import json
import requests

URL_API = "https://odre.opendatasoft.com/api/records/1.0/search/?dataset=eco2mix-national-tr&rows=1000"

FICHIER_SORTIE = "data/eco2mix-national.json"


def telecharger_json(url, chemin_fichier):
    reponse = requests.get(url, timeout=15)
    reponse.raise_for_status()

    os.makedirs(os.path.dirname(chemin_fichier), exist_ok=True)

    with open(chemin_fichier, "w", encoding="utf-8") as f:
        json.dump(reponse.json(), f, indent=2, ensure_ascii=False)

    return chemin_fichier


if __name__ == "__main__":
    print("Téléchargement des données RTE éCO2mix (via data.gouv.fr/ODRÉ)...")
    chemin = telecharger_json(URL_API, FICHIER_SORTIE)
    print(f"Terminé : fichier enregistré sous {chemin}")