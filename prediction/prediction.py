import glob
import joblib


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


if __name__ == "__main__":

    modele = charger_dernier_modele("../models")
    print(modele)