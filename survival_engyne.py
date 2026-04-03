import pandas as pd
import sqlite3
from lifelines import KaplanMeierFitter
import matplotlib.pyplot as plt

def calculer_survie():
    conn = sqlite3.connect('luxury_inventory.db')
    df = pd.read_sql("SELECT * FROM inventory", conn)
    conn.close()

    kmf = KaplanMeierFitter()
    
    # On entraîne le modèle : 
    # Durée = jours_en_rayon / Événement = est_vendu
    kmf.fit(df['jours_en_rayon'], event_observed=df['est_vendu'], label="Probabilité de vente au prix fort")
    
    # On peut maintenant prédire ! 
    # Quelle est la probabilité de vendre après 90 jours ?
    prob_90 = kmf.predict(90)
    print(f"Probabilité de survie en stock après 90 jours : {prob_90:.2%}")
    
    return kmf

if __name__ == "__main__":
    calculer_survie()