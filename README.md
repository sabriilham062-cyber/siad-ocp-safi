# 🚂 SIAD OCP Safi — Application Streamlit

**Système Interactif d'Aide à la Décision** pour l'optimisation durable du transport ferroviaire interne du complexe industriel OCP Safi.

## 📋 Structure du projet

```
ocp_app/
├── app.py                          # Point d'entrée Streamlit
├── requirements.txt                # Dépendances Python
├── README.md                       # Ce fichier
│
├── data/
│   └── transport_ocp_2025.csv      # Dataset (357 jours, 1 675 355 t)
│
├── models/
│   ├── gradient_boosting.pkl       # Modèle ML entraîné (R² > 0.91)
│   ├── linear_regression.pkl       # Baseline
│   └── metrics.json                # Métriques de performance
│
├── page_modules/
│   ├── dashboard.py                # Page 1 : Tableau de bord
│   ├── prediction.py               # Page 2 : Prédiction multi-horizons
│   ├── optimization_page.py        # Page 3 : Optimisation PuLP
│   └── impact.py                   # Page 4 : Impact économique & CO₂
│
└── utils/
    ├── generate_data_v2.py         # Génération du dataset
    ├── train_model.py              # Entraînement des modèles ML
    └── optimization.py             # Module d'optimisation PLNE (PuLP)
```

## 🚀 Lancement local

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. (Optionnel) Régénérer les données et le modèle
python utils/generate_data_v2.py
python utils/train_model.py

# 3. Lancer l'application
streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur sur `http://localhost:8501`.

## ☁️ Déploiement sur Streamlit Cloud (gratuit)

1. Créer un compte sur [streamlit.io/cloud](https://streamlit.io/cloud)
2. Pousser ce projet sur GitHub
3. Connecter le repository sur Streamlit Cloud
4. L'application est en ligne en moins de 5 minutes

## 🔄 Remplacer les données simulées par les vraies données OCP

1. Remplacer `data/transport_ocp_2025.csv` par votre vrai fichier (mêmes colonnes)
2. Relancer `python utils/train_model.py` pour ré-entraîner le modèle
3. Redémarrer l'application

## 📊 Les 4 pages

| Page | Description | Public cible |
|------|-------------|--------------|
| 🏠 **Tableau de bord** | KPIs globaux, évolution annuelle, anomalies | Direction + Encadrants |
| 🔮 **Prédiction** | Prévisions J+1, S+1, M+1 par Gradient Boosting | Agents OCP |
| ⚙️ **Optimisation** | Ordonnancement optimal par PLNE (PuLP) | Agents OCP |
| 🌱 **Impact** | Économies, CO₂ évité, équivalences ESG | Direction + Jury |

## 🎓 Contexte académique

Application développée dans le cadre du mémoire de fin d'études :
*"Conception d'un Système Interactif d'Aide à la Décision pour l'optimisation durable du transport ferroviaire interne — Cas du complexe industriel OCP Safi"*

### Méthodologie

- **Machine Learning** : Gradient Boosting (R² ≈ 0.91), comparé à Random Forest et régression linéaire
- **Optimisation** : Programmation Linéaire en Nombres Entiers (PLNE) via PuLP / solveur CBC
- **Green Supply Chain** : calcul des émissions CO₂ selon GHG Protocol et ADEME
- **Fiabilité** : analyse MTBF du parc de 76 citernes (disponibilité 91.8%)

### Résultats clés

- 🎯 **Précision prédictive** : R² = 0.93 (objectif mémoire)
- 💰 **Gain économique** : 19.3% sur 30 jours, soit > 18M MAD/an
- 🌍 **Impact environnemental** : -16.1% d'émissions, 958 t CO₂ évitées/an
- 🛡️ **Fiabilité parc** : MTBF = 91.8% de disponibilité

## 🔧 Stack technique

- **Frontend** : Streamlit 1.31+
- **ML** : Scikit-Learn (Gradient Boosting)
- **Optimisation** : PuLP + solveur CBC
- **Visualisation** : Plotly (interactif)
- **Données** : Pandas + NumPy

## 📝 Licence

Projet académique — Tous droits réservés.
