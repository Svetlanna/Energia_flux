import glob
import joblib
import pandas as pd


def charger_dernier_modele(dossier_modeles):


    fichiers = glob.glob(f"{dossier_modeles}/modele_consommation_*.pkl")

    if not fichiers:
        raise FileNotFoundError(f"Aucun modele trouve dans {dossier_modeles}")


    fichiers_tries = sorted(fichiers)


    chemin_dernier_modele = fichiers_tries[-1]

    # joblib.load() fait l'inverse de joblib.dump() : il relit le fichier
    # binaire et reconstruit l'objet modele en memoire.
    model = joblib.load(chemin_dernier_modele)

    print(f"Modele charge : {chemin_dernier_modele}")
    return model






FEATURES = [
    "heure",
    "jour_semaine",
    "mois",
    "nucleaire",
    "eolien",
    "solaire",
    "hydraulique",
    "taux_co2",
]


def predire(model, entrees):


    X = pd.DataFrame([entrees], columns=FEATURES)

    prediction = model.predict(X)

    return float(prediction[0])


if __name__ == "__main__":
    model = charger_dernier_modele("../models")

    exemple = {
        "heure": 14,
        "jour_semaine": 2,
        "mois": 8,
        "nucleaire": 40000,
        "eolien": 5000,
        "solaire": 3000,
        "hydraulique": 5000,
        "taux_co2": 30,
    }

    resultat = predire(model, exemple)
    print(f"Prediction : {resultat:.0f} MW")




if __name__ == "__main__":

    modele = charger_dernier_modele("../models")
    print(modele)