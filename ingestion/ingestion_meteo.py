import os
import json
import csv

FICHIER_ENTREE = "../extraction/data/Open-Meteo.json"
FICHIER_SORTIE = "../data/meteo-unifie.csv"


def ingerer_meteo(fichier_entree=FICHIER_ENTREE, fichier_sortie=FICHIER_SORTIE):
    with open(fichier_entree, "r", encoding="utf-8") as f:
        data = json.load(f)

    horaire = data["hourly"]
    dates = horaire["time"]
    temperatures = horaire["temperature_2m"]
    humidites = horaire["relative_humidity_2m"]

    os.makedirs(os.path.dirname(fichier_sortie), exist_ok=True)
    with open(fichier_sortie, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date_heure", "temperature", "humidite"])
        for date_heure, temperature, humidite in zip(dates, temperatures, humidites):
            writer.writerow([date_heure, temperature, humidite])

    return len(dates), fichier_sortie


if __name__ == "__main__":
    print("Ingestion des donnees meteo (Open-Meteo)...")
    nb_lignes, chemin = ingerer_meteo()
    print(f"  {nb_lignes} ligne(s) converties")
    print(f"Termine : fichier unifie enregistre sous {chemin}")