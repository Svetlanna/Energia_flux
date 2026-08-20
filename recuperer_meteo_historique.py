import os
import json
import requests

URL_API_METEO_HISTORIQUE = (
    "https://archive-api.open-meteo.com/v1/archive"
    "?latitude=48.85&longitude=2.35"
    "&start_date=2026-07-01&end_date=2026-08-19"
    "&hourly=temperature_2m,relative_humidity_2m"
)
FICHIER_SORTIE = "extraction/data/Open-Meteo.json"


def telecharger_meteo_historique(url, chemin_fichier):
    reponse = requests.get(url, timeout=30)
    reponse.raise_for_status()

    os.makedirs(os.path.dirname(chemin_fichier), exist_ok=True)
    with open(chemin_fichier, "w", encoding="utf-8") as f:
        json.dump(reponse.json(), f, indent=2, ensure_ascii=False)

    return chemin_fichier


if __name__ == "__main__":
    print("Telechargement de la meteo historique")
    chemin = telecharger_meteo_historique(URL_API_METEO_HISTORIQUE, FICHIER_SORTIE)
    print(f"Termine : fichier enregistre sous {chemin}")