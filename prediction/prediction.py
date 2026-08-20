import glob
import joblib
import pandas as pd
import os


def charger_dernier_modele(dossier_modeles):
    fichiers = glob.glob(f"{dossier_modeles}/modele_consommation_*.pkl")

    if not fichiers:
        raise FileNotFoundError(f"Aucun modele trouve dans {dossier_modeles}")

    fichiers_tries = sorted(fichiers)
    chemin_dernier_modele = fichiers_tries[-1]
    model = joblib.load(chemin_dernier_modele)

    nom_fichier = os.path.basename(chemin_dernier_modele)

    version = nom_fichier.replace(".pkl", "")

    print(f"Modele charge : {chemin_dernier_modele}")
    return model, version






FEATURES = ["heure", "jour_semaine", "mois", "weekend", "temperature", "humidite"]


def predire(model, entrees):


    X = pd.DataFrame([entrees], columns=FEATURES)

    prediction = model.predict(X)

    return float(prediction[0])


if __name__ == "__main__":
    model, version = charger_dernier_modele("../models")
    
    exemple = {
        "heure": 14, "jour_semaine": 2, "mois": 8,
        "weekend": 0, "temperature": 24.5, "humidite": 55,
    }

    resultat = predire(model, exemple)
    print(f"Modele utilise : {version}")
    print(f"Prediction : {resultat:.0f} MW")