import os
import json
import csv

FICHIER_ENTREE = "data/eco2mix-national.json"
FICHIER_SORTIE = "data/eco2mix-unifie.csv"

# champs obligatoires un enregistrement sans ces valeurs est inexploitable
CHAMPS_OBLIGATOIRES = ["date_heure", "consommation"]

# colonnes du format unifie dans l'ordre de sortie
COLONNES_UNIFIEES = [
    "date_heure",
    "consommation",
    "nucleaire",
    "eolien",
    "solaire",
    "hydraulique",
    "taux_co2",
]


def valider_enregistrement(fields):

    # Verifie qu'un enregistrement contient les champs obligatoires et non nuls.


    for champ in CHAMPS_OBLIGATOIRES:
        if fields.get(champ) is None:
            return False
    return True


def convertir_enregistrement(fields):

    return {colonne: fields.get(colonne) for colonne in COLONNES_UNIFIEES}


def ingerer(fichier_entree, fichier_sortie):

    with open(fichier_entree, "r", encoding="utf-8") as f:
        donnees_brutes = json.load(f)

    records = donnees_brutes.get("records", [])
    if not records:
        raise ValueError(f"Aucun 'records' trouve dans {fichier_entree} — format inattendu.")

    lignes_valides = []
    nb_rejetes = 0

    for record in records:
        fields = record.get("fields", {})

        # validation du format
        if not valider_enregistrement(fields):
            nb_rejetes += 1
            continue

        #conversion vers un format unifie
        lignes_valides.append(convertir_enregistrement(fields))

    #sauvegarde intermediaire
    os.makedirs(os.path.dirname(fichier_sortie), exist_ok=True)
    with open(fichier_sortie, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLONNES_UNIFIEES)
        writer.writeheader()
        writer.writerows(lignes_valides)

    return len(lignes_valides), nb_rejetes, fichier_sortie


if __name__ == "__main__":
    print("Ingestion et validation des donnees eCO2mix...")
    nb_ok, nb_ko, chemin = ingerer(FICHIER_ENTREE, FICHIER_SORTIE)
    print(f"  {nb_ok} enregistrement(s) valide(s), {nb_ko} rejete(s)")
    print(f"Termine : fichier unifie enregistre sous {chemin}")
