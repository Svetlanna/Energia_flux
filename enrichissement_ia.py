import os

import pandas as pd
import mysql.connector
from dotenv import load_dotenv
from google import genai

load_dotenv()

SEUIL_ECART_POURCENT = 10.0


def connecter_db():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        port=os.environ["DB_PORT"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )


def detecter_anomalies(connexion):
    df = pd.read_sql("SELECT date_heure, consommation FROM consommation", connexion)
    df["date_heure"] = pd.to_datetime(df["date_heure"])
    df["date_jour"] = df["date_heure"].dt.date

    par_jour = df.groupby("date_jour")["consommation"].mean().reset_index()
    par_jour.columns = ["date_jour", "consommation_moyenne_mw"]

    par_jour["moyenne_mobile_7j_mw"] = (
        par_jour["consommation_moyenne_mw"].rolling(window=7, min_periods=3).mean()
    )
    par_jour["ecart_pourcent"] = (
        (par_jour["consommation_moyenne_mw"] - par_jour["moyenne_mobile_7j_mw"])
        / par_jour["moyenne_mobile_7j_mw"] * 100
    )

    anomalies = par_jour[par_jour["ecart_pourcent"].abs() > SEUIL_ECART_POURCENT]
    return anomalies.dropna(subset=["ecart_pourcent"])


def generer_commentaire(client, date_jour, ecart_pourcent):
    sens = "au-dessus" if ecart_pourcent > 0 else "en-dessous"
    prompt = (
        f"Le {date_jour}, la consommation electrique francaise etait "
        f"{abs(ecart_pourcent):.1f}% {sens} de sa moyenne mobile sur 7 jours. "
        "En une phrase courte, propose une explication plausible "
        "(meteo extreme, jour ferie, evenement, greve, etc.), "
        "en precisant que c'est une hypothese non verifiee."
    )
    reponse = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    return reponse.text


def enregistrer(connexion, ligne, commentaire):
    curseur = connexion.cursor()
    curseur.execute(
        """
        INSERT INTO evenement_exceptionnel
            (date_jour, consommation_moyenne_mw, moyenne_mobile_7j_mw, ecart_pourcent, commentaire_ia)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            ligne["date_jour"],
            ligne["consommation_moyenne_mw"],
            ligne["moyenne_mobile_7j_mw"],
            ligne["ecart_pourcent"],
            commentaire,
        ),
    )
    connexion.commit()
    curseur.close()


if __name__ == "__main__":
    client = genai.Client()
    connexion = connecter_db()

    anomalies = detecter_anomalies(connexion)
    print(f"{len(anomalies)} jour(s) anormal(aux) detecte(s)")

    for _, ligne in anomalies.iterrows():
        commentaire = generer_commentaire(client, ligne["date_jour"], ligne["ecart_pourcent"])
        enregistrer(connexion, ligne, commentaire)
        print(f"  {ligne['date_jour']} ({ligne['ecart_pourcent']:.1f}%) : {commentaire}")

    connexion.close()
