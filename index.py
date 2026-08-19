
from extraction.EDF import telecharger_json, URL_API, FICHIER_SORTIE as JSON_BRUT
from ingestion.ingestion import ingerer, FICHIER_SORTIE as CSV_UNIFIE
from etl.Etl import executer_etl

# chemin relatif a la racine du projet (index.py est lance depuis la racine,
# comme JSON_BRUT et CSV_UNIFIE ci-dessus ne pas reutiliser les constantes
# de etl/Etl.py, qui elles supposent d'etre lancees depuis le dossier etl
DOSSIER_DATALAKE = "data/datalake"


def main():

    # extraction
    print("API gouvernement")
    chemin_json = telecharger_json(URL_API, JSON_BRUT)
    print(f"fichier brut : {chemin_json}")

    # ingestion et validation
    print("Ingestion et validation")
    nb_ok, nb_ko, chemin_csv = ingerer(JSON_BRUT, CSV_UNIFIE)
    print(f"  {nb_ok} lignes valides, {nb_ko} rejetees")

    # etl et stockage (MySQL + datalake)
    print("ETL et stockage")
    nb_inserees, nb_ignorees, chemin_datalake = executer_etl(chemin_csv, DOSSIER_DATALAKE)
    print(f"  MySQL : {nb_inserees} ligne(s) inseree(s), {nb_ignorees} deja presente(s)")
    print(f"  Datalake : copie enregistree sous {chemin_datalake}")


if __name__ == "__main__":
    main()
