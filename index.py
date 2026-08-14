
from extraction.EDF import telecharger_json, URL_API, FICHIER_SORTIE as JSON_BRUT
from ingestion.ingestion import ingerer, FICHIER_SORTIE as CSV_UNIFIE


def main():

    # extraction
    print("API gouvernement")
    chemin_json = telecharger_json(URL_API, JSON_BRUT)
    print(f"fichier brut : {chemin_json}")

    # ingestion et validation
    print("Ingestion et validation")
    nb_ok, nb_ko, chemin_csv = ingerer(JSON_BRUT, CSV_UNIFIE)
    print(f"  {nb_ok} lignes valides, {nb_ko} rejetees")



if __name__ == "__main__":
    main()
