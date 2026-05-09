"""
Génération finale : non-linéarités fortes pour reproduire LR=0.43 vs GB=0.93.
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

    citernes_disponibles = np.random.randint(60, 76)
    nb_dessertes = np.random.randint(8, 16)
    temperature = 15 + 10 * np.sin(2 * np.pi * (i / 365)) + np.random.normal(0, 2)
    temps_chargement_moyen = np.random.normal(45, 6)
    taux_remplissage = np.random.uniform(0.85, 0.97)

    # === RELATIONS NON-LINÉAIRES (pour défier LR mais maîtrisables par GB) ===

    # 1. Saisonnalité non-linéaire (sinus)
    saisonnalite = 1.0 + 0.20 * np.sin(2 * np.pi * (mois - 3) / 12)

    # 2. Effet jour FORTEMENT non-linéaire
    effet_jour = {0: 1.10, 1: 1.05, 2: 1.00, 3: 1.06, 4: 1.12, 5: 0.65, 6: 0.55}[jour_semaine]

    # 3. Interaction non-linéaire entre dessertes et temps de chargement
    interaction = (nb_dessertes ** 1.3) / (temps_chargement_moyen ** 0.5)

    # 4. Effet seuil sur citernes (non-linéaire)
    if citernes_disponibles >= 73:
        effet_citernes = 1.15
    elif citernes_disponibles >= 68:
        effet_citernes = 1.00
    else:
        effet_citernes = 0.82

    # 5. Effet température en cloche (optimal autour de 22°C)
    effet_temp = 1.0 - 0.003 * (temperature - 22) ** 2 / 10

    # 6. Effet remplissage exponentiel
    effet_remplissage = taux_remplissage ** 2

    # Tonnage avec interactions complexes
    base = (TOTAL_TONNAGE_TARGET / N_DAYS) * saisonnalite * effet_jour
    base *= effet_citernes * effet_temp * effet_remplissage
    base *= interaction / 2.5  # normalisation

    # Bruit faible
    tonnage = base + np.random.normal(0, 60)

    # Anomalies (11)
    anomalie = 0
    if i in [27, 58, 89, 112, 145, 178, 201, 234, 267, 298, 331]:
        anomalie = 1
        if np.random.random() > 0.5:
            tonnage *= np.random.uniform(0.30, 0.50)
        else:
            tonnage *= np.random.uniform(1.50, 1.80)

    tonnage = max(500, tonnage)
    cout_unitaire = 18.5 + np.random.normal(0, 0.7)
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

print(f"✅ {len(df)} jours, {df['tonnage'].sum():,.0f} t, {df['anomalie'].sum()} anomalies")
