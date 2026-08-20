from extraction.EDF import telecharger_json, URL_API, FICHIER_SORTIE as JSON_BRUT
from ingestion.ingestion import ingerer, FICHIER_SORTIE as CSV_UNIFIE
from etl.Etl import executer_etl
from ingestion.ingestion_meteo import ingerer_meteo
from etl_meteo import connecter_db as connecter_db_meteo, charger_lignes_csv, inserer_meteo

DOSSIER_DATALAKE = "data/datalake"


def main():
    # extraction et ingestion RTE
    print("API gouvernement")
    chemin_json = telecharger_json(URL_API, JSON_BRUT)
    print(f"fichier brut : {chemin_json}")

    print("Ingestion et validation")
    nb_ok, nb_ko, chemin_csv = ingerer(JSON_BRUT, CSV_UNIFIE)
    print(f"  {nb_ok} lignes valides, {nb_ko} rejetees")

    print("ETL et stockage")
    nb_inserees, nb_ignorees, chemin_datalake = executer_etl(chemin_csv, DOSSIER_DATALAKE)
    print(f"  MySQL : {nb_inserees} ligne(s) inseree(s), {nb_ignorees} deja presente(s)")
    print(f"  Datalake : copie enregistree sous {chemin_datalake}")

    # ingestion meteo (chemins explicites, relatifs a la racine)
    print("Ingestion meteo")
    nb_lignes_meteo, chemin_meteo_csv = ingerer_meteo(
        fichier_entree="extraction/data/Open-Meteo.json",
        fichier_sortie="data/meteo-unifie.csv",
    )
    print(f"  {nb_lignes_meteo} ligne(s) convertie(s)")

    # etl meteo
    print("ETL meteo")
    lignes_meteo = charger_lignes_csv(chemin_meteo_csv)
    connexion_meteo = connecter_db_meteo()
    nb_meteo_inserees = inserer_meteo(connexion_meteo, lignes_meteo)
    connexion_meteo.close()
    print(f"  MySQL meteo : {nb_meteo_inserees} ligne(s) inseree(s)")


if __name__ == "__main__":
    main()