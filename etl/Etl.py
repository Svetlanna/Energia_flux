# lit le CSV unifie (ingestion.py)
#   1. Stocke chaque ligne dans MySQL table consommation.
#   2. Garde une copie horodatee dans le datalake (historique brut des extractions).

# Les identifiants MySQL sont lus depuis les variables d'environnement (.env),
# jamais ecrits en dur dans le code.

import os
import csv
import shutil
from datetime import datetime, timezone

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

FICHIER_ENTREE = "../data/eco2mix-unifie.csv"
DOSSIER_DATALAKE = "../data/datalake"


def connecter_db():

    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        port=os.environ["DB_PORT"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )


def charger_lignes_csv(fichier_entree):

    # Lit le CSV unifie et retourne la liste des lignes

    with open(fichier_entree, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def inserer_dans_mysql(connexion, lignes):

    curseur = connexion.cursor()

    requete = """
        INSERT IGNORE INTO consommation
            (date_heure, consommation, nucleaire, eolien, solaire, hydraulique, taux_co2)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    nb_inserees = 0
    for ligne in lignes:
        valeurs = (
            ligne["date_heure"],
            ligne["consommation"] or None,
            ligne["nucleaire"] or None,
            ligne["eolien"] or None,
            ligne["solaire"] or None,
            ligne["hydraulique"] or None,
            ligne["taux_co2"] or None,
        )
        curseur.execute(requete, valeurs)
        if curseur.rowcount == 1:
            nb_inserees += 1

    connexion.commit()
    curseur.close()

    nb_ignorees = len(lignes) - nb_inserees
    return nb_inserees, nb_ignorees


def sauvegarder_datalake(fichier_entree, dossier_datalake):

    # copie le CSV unifie dans le datalake, avec un nom horodate, pour garder
    # un historique des extractions

    os.makedirs(dossier_datalake, exist_ok=True)
    horodatage = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    chemin_copie = os.path.join(dossier_datalake, f"eco2mix-{horodatage}.csv")
    shutil.copyfile(fichier_entree, chemin_copie)
    return chemin_copie


def executer_etl(fichier_entree, dossier_datalake):

    # enchaine le chargement du CSV, l'insertion MySQL et la copie datalake.
    lignes = charger_lignes_csv(fichier_entree)

    connexion = connecter_db()
    nb_inserees, nb_ignorees = inserer_dans_mysql(connexion, lignes)
    connexion.close()

    chemin_datalake = sauvegarder_datalake(fichier_entree, dossier_datalake)

    return nb_inserees, nb_ignorees, chemin_datalake


if __name__ == "__main__":
    print("ETL et stockage...")
    nb_ok, nb_ignore, chemin = executer_etl(FICHIER_ENTREE, DOSSIER_DATALAKE)
    print(f"  MySQL : {nb_ok} ligne(s) inseree(s), {nb_ignore} deja presente(s)")
    print(f"  Datalake : copie enregistree sous {chemin}")
    print("Termine.")