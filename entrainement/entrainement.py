import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import os
import json
import requests
import joblib

import mysql.connector
from dotenv import load_dotenv

load_dotenv()



def connect_db():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        port=os.environ["DB_PORT"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"]
    )
connexion = connect_db()
df = pd.read_sql("SELECT * FROM consommation",connexion)
print(df)
connexion.close()

