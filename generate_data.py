"""
Génération de données simulées calibrées sur les chiffres réels du mémoire OCP Safi.
Cible : 357 jours, 1 675 355 tonnes, R² = 0.93 atteignable, 11 anomalies.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

N_DAYS = 357
TOTAL_TONNAGE_TARGET = 1_675_355
START_DATE = datetime(2025, 1, 1)

dates = [START_DATE + timedelta(days=i) for i in range(N_DAYS)]
data = []

for i, date in enumerate(dates):
    jour_semaine = date.weekday()
    mois = date.month
    jour_mois = date.day
    semaine_annee = date.isocalendar()[1]
    est_weekend = 1 if jour_semaine >= 5 else 0

    saisonnalite = 1.0 + 0.18 * np.sin(2 * np.pi * (mois - 3) / 12)
    effet_jour = {0: 1.08, 1: 1.04, 2: 1.00, 3: 1.05, 4: 1.10, 5: 0.78, 6: 0.70}[jour_semaine]

    citernes_disponibles = np.random.randint(65, 76)
    nb_dessertes = np.random.randint(8, 16)
    temperature = 15 + 10 * np.sin(2 * np.pi * (i / 365)) + np.random.normal(0, 2)
    temps_chargement_moyen = np.random.normal(45, 5)
    taux_remplissage = np.random.uniform(0.88, 0.97)

    base = (TOTAL_TONNAGE_TARGET / N_DAYS) * saisonnalite * effet_jour
    base *= (citernes_disponibles / 70) * (nb_dessertes / 12) * taux_remplissage
    base *= (50 / max(temps_chargement_moyen, 35))
    tonnage = base + np.random.normal(0, 80)

    anomalie = 0
    if i in [27, 58, 89, 112, 145, 178, 201, 234, 267, 298, 331]:
        anomalie = 1
        if np.random.random() > 0.5:
            tonnage *= np.random.uniform(0.35, 0.55)
        else:
            tonnage *= np.random.uniform(1.45, 1.70)

    tonnage = max(500, tonnage)
    cout_unitaire = 18.5 + np.random.normal(0, 0.8)
    cout_total = tonnage * cout_unitaire
    co2_kg = tonnage * 22 * 35 / 1000

    data.append({
        'date': date, 'jour_semaine': jour_semaine, 'mois': mois,
        'jour_mois': jour_mois, 'semaine_annee': semaine_annee, 'est_weekend': est_weekend,
        'citernes_disponibles': citernes_disponibles, 'nb_dessertes': nb_dessertes,
        'temperature': round(temperature, 1),
        'temps_chargement_moyen': round(temps_chargement_moyen, 1),
        'taux_remplissage': round(taux_remplissage, 3),
        'tonnage': round(tonnage, 1),
        'cout_unitaire_mad': round(cout_unitaire, 2),
        'cout_total_mad': round(cout_total, 2),
        'co2_kg': round(co2_kg, 1), 'anomalie': anomalie
    })

df = pd.DataFrame(data)
ratio = TOTAL_TONNAGE_TARGET / df['tonnage'].sum()
df['tonnage'] = (df['tonnage'] * ratio).round(1)
df['cout_total_mad'] = (df['tonnage'] * df['cout_unitaire_mad']).round(2)
df['co2_kg'] = (df['tonnage'] * 22 * 35 / 1000).round(1)
df.to_csv('/home/claude/ocp_app/data/transport_ocp_2025.csv', index=False)

print(f"✅ Dataset : {len(df)} jours, {df['tonnage'].sum():,.0f} t, {df['anomalie'].sum()} anomalies")
