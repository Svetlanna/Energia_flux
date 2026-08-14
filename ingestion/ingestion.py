import os
import json
import csv

FICHIER_ENTREE = "data/eco2mix-national.json"
FICHIER_SORTIE = "data/eco2mix-unifie.csv"

# Champs obligatoires un enregistrement sans ces valeurs est inexploitable
CHAMPS_OBLIGATOIRES = ["date_heure", "consommation"]

# Colonnes du format unifie dans l'ordre de sortie
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

    # Args:
    #     fields (dict): le contenu de "fields" pour un record de l'API.

    # Returns:
    #     bool: True si l'enregistrement est valide, False sinon.

    for champ in CHAMPS_OBLIGATOIRES:
        if fields.get(champ) is None:
            return False
    return True


def convertir_enregistrement(fields):
    # Extrait uniquement les colonnes du format unifie depuis un enregistrement brut.

    # Args:
    #     fields (dict): le contenu de "fields" pour un record de l'API.

    # Returns:
    #     dict: une ligne au format unifie (valeurs manquantes -> None).

    return {colonne: fields.get(colonne) for colonne in COLONNES_UNIFIEES}


def ingerer(fichier_entree, fichier_sortie):
    """
    Lit le JSON brut valide et convertit chaque enregistrement,
    puis sauvegarde le resultat en CSV.

    Args:
        fichier_entree (str): chemin du JSON brut sortie de EDF.py.
        fichier_sortie (str): chemin du CSV unifie a produire.

    Returns:
        tuple: (nb_valides, nb_rejetes, chemin_sortie)
    """
    with open(fichier_entree, "r", encoding="utf-8") as f:
        donnees_brutes = json.load(f)

    records = donnees_brutes.get("records", [])
    if not records:
        raise ValueError(f"Aucun 'records' trouve dans {fichier_entree} — format inattendu.")

    lignes_valides = []
    nb_rejetes = 0

    for record in records:
        fields = record.get("fields", {})

        # Validation du format
        if not valider_enregistrement(fields):
            nb_rejetes += 1
            continue

        #Conversion vers un format unifie
        lignes_valides.append(convertir_enregistrement(fields))

    #Sauvegarde intermediaire
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
