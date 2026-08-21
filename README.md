# EnergIA

Pipeline de prédiction de la consommation électrique française, à partir des données RTE éCO2mix et Open-Meteo. Projet réalisé dans le cadre du titre RNCP "Développeur.se en intelligence artificielle" (encadrant : Thomas Viviani)

## Ce que fait le projet

Le pipeline va chercher des données brutes sur Internet (consommation électrique + météo), les nettoie, les stocke en base MySQL, entraîne un modèle de machine learning pour prédire la consommation future, puis expose ce modèle via une API. Une passerelle (gateway) sert de point d'entrée unique, et un adaptateur relie les prédictions au moteur de simulation nucléaire fourni par le professeur. Un module d'enrichissement détecte les jours de consommation anormale et demande une explication à une IA (Gemini)

## Architecture — le pipeline complet

```
extraction -> ingestion -> ETL -> entrainement -> chargement des tables -> prediction -> adaptateur -> gateway
```

1. **Extraction** (`extraction/EDF.py`) — télécharge les données brutes RTE et météo (JSON), sans les transformer
2. **Ingestion** (`ingestion/ingestion.py`, `ingestion/ingestion_meteo.py`) — valide et nettoie le JSON, produit des CSV unifiés. `recuperer_meteo_historique.py` est un script à part, utilisé ponctuellement pour récupérer un historique météo passé (API Archive Open-Meteo)
3. **ETL** (`etl/Etl.py`, `etl_meteo.py`) — charge les CSV dans MySQL (tables `consommation` et `meteo`), avec une copie brute archivée dans `data/datalake/`
4. **Entraînement** (`entrainement/entrainement.py`) — joint consommation et météo, construit les features (heure, jour_semaine, mois, weekend, temperature, humidite), entraîne un `RandomForestRegressor`, sauvegarde le modèle (`.pkl` + `.json` dans `models/`)
5. **Chargement des tables de référence** — `charger_modele.py` enregistre les modèles entraînés dans la table `modele` (traçabilité). `charger_region.py` enregistre les profils régionaux (fichier fourni par le professeur) dans la table `region`
6. **Prédiction** (`prediction/prediction.py`, `prediction/api.py`) — service FastAPI qui charge le dernier modèle et répond aux requêtes `POST /predict`, avec cache (10 min) et journalisation de chaque prédiction dans la table `prediction`
7. **Gateway** (`gateway/server.js`) — service Express qui reçoit les requêtes des clients (Bruno, futur front) sur `POST /api/prediction` et les relaie vers l'API FastAPI
8. **Adaptateur** (`adaptateur_moteur.py`) — transforme une prédiction en format compris par le moteur nucléaire prescriptif du professeur (`{region_id, additional_demand_mw}`)
9. **Enrichissement IA** (`enrichissement_ia.py`) — détecte les jours où la consommation s'écarte de plus de 10% de sa moyenne mobile sur 7 jours, et enregistre une explication générée par Gemini dans la table `evenement_exceptionnel`

`index.py` automatise les étapes 1 à 3 (extraction + ingestion + ETL, RTE et météo). Les étapes 4 à 9 se lancent manuellement, car ce sont des opérations moins fréquentes

## Structure des dossiers

```
extraction/         telechargement des donnees brutes (RTE, meteo)
ingestion/           validation + nettoyage -> CSV unifie
etl/                 chargement de consommation dans MySQL
etl_meteo.py         chargement de meteo dans MySQL
entrainement/         entrainement du modele
models/               modeles entraines (.pkl + .json), non versionne dans git
prediction/           API FastAPI de prediction
gateway/              passerelle Express (point d'entree)
adaptateur_moteur.py  lien avec le moteur nucleaire du professeur
enrichissement_ia.py  detection d'anomalies + explication Gemini
charger_modele.py     enregistre les modeles entraines en base
charger_region.py     enregistre les profils regionaux en base
data/                 CSV unifies + archive datalake, non versionne dans git
Schema.sql             script de creation de la base MySQL
DB_Diagrame.png        schema visuel de la base
index.py               orchestre extraction + ingestion + ETL
```

## Prérequis

- Python 3.11
- Node.js (pour le gateway)
- MySQL (base `energia_flux`, voir `Schema.sql`)
- Une clé API Gemini personnelle (voir plus bas)

## Installation

Côté Python, à la racine du projet :

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install google-genai
```

(`google-genai` n'est pas encore dans `requirements.txt` mais il est nécessaire pour `enrichissement_ia.py` — pense à l'ajouter dans `requirements.txt` pour que l'équipe n'ait pas à s'en souvenir.)

Côté Node, dans `gateway/` 

```
cd gateway
npm install
```

## Configuration — fichier `.env`

Chaque membre de l'équipe crée son propre fichier `.env` à la racine du projet (jamais commité dans git) avec ces variables 

```
DB_HOST=...
DB_USER=...
DB_PORT=...
DB_PASSWORD=...
DB_NAME=energia_flux
GEMINI_API_KEY=...
```

Chaque personne doit créer **sa propre** clé Gemini (gratuite, sans carte bancaire) sur https://ai.google.dev/gemini-api/docs/api-key — ne pas partager une même clé entre plusieurs membres de l'équipe

## Créer la base de données

```
mysql -u <utilisateur> -p < Schema.sql
```

Voir `DB_Diagrame.png` pour le schéma visuel des 6 tables (`consommation`, `meteo`, `modele`, `prediction`, `region`, `evenement_exceptionnel`)

## Lancer le projet

Trois terminaux séparés 

**Terminal 1 — mise à jour des données** (à la racine du projet) 
```
python index.py
```

**Terminal 2 — API de prédiction** (dans `prediction/`) 
```
uvicorn api:app --reload
```
Écoute sur `http://127.0.0.1:8000` (Swagger sur `/docs`)

**Terminal 3 — gateway** (dans `gateway/`) 
```
node server.js
```
Écoute sur `http://127.0.0.1:3000`

## Tester avec Bruno

Requête `POST http://127.0.0.1:3000/api/prediction`, body JSON 

```json
{
  "heure": 14,
  "jour_semaine": 2,
  "mois": 8,
  "weekend": 0,
  "temperature": 24.5,
  "humidite": 55
}
```

`heure` : 0-23. `jour_semaine` : 0 = lundi ... 6 = dimanche. `mois` : 1-12. `weekend` : 0 ou 1. `temperature` en °C, `humidite` en %

La première requête renvoie `"depuis_cache": false`. La même requête répétée dans les 10 minutes renvoie `"depuis_cache": true`
