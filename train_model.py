"""Entraînement final : Gradient Boosting avec gestion des anomalies."""
import pandas as pd
import numpy as np
import joblib
import json
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, cross_val_score, train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

df = pd.read_csv('/home/claude/ocp_app/data/transport_ocp_2025.csv')
df['date'] = pd.to_datetime(df['date'])

features = ['jour_semaine', 'mois', 'jour_mois', 'semaine_annee', 'est_weekend',
            'citernes_disponibles', 'nb_dessertes', 'temperature',
            'temps_chargement_moyen', 'taux_remplissage']

df_normal = df[df['anomalie'] == 0].copy()
X = df_normal[features]
y = df_normal['tonnage']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("=" * 60)
print("COMPARAISON DES MODÈLES (sur données normales)")
print("=" * 60)

lr = LinearRegression()
lr.fit(X_train, y_train)
r2_lr = r2_score(y_test, lr.predict(X_test))
print(f"\n📈 Régression linéaire : R² = {r2_lr:.3f}")

rf = RandomForestRegressor(n_estimators=300, max_depth=15, random_state=42)
rf.fit(X_train, y_train)
r2_rf = r2_score(y_test, rf.predict(X_test))
print(f"🌲 Random Forest      : R² = {r2_rf:.3f}")

gb = GradientBoostingRegressor(n_estimators=500, max_depth=6, learning_rate=0.05,
                                min_samples_split=4, random_state=42)
gb.fit(X_train, y_train)
y_pred_gb = gb.predict(X_test)
r2_gb = r2_score(y_test, y_pred_gb)
mae_gb = mean_absolute_error(y_test, y_pred_gb)
rmse_gb = np.sqrt(mean_squared_error(y_test, y_pred_gb))

print(f"🚀 Gradient Boosting  : R² = {r2_gb:.3f}  MAE = {mae_gb:.0f} t  RMSE = {rmse_gb:.0f} t")

X_full = df[features]
y_full = df['tonnage']
r2_full = r2_score(y_full, gb.predict(X_full))
print(f"\n📊 R² sur dataset complet : {r2_full:.3f}")

tscv = TimeSeriesSplit(n_splits=5)
cv_scores = cross_val_score(gb, X, y, cv=tscv, scoring='r2')
print(f"🔍 CV temporelle 5-fold : R² = {cv_scores.mean():.3f}")

importance_df = pd.DataFrame({'feature': features, 'importance': gb.feature_importances_}).sort_values('importance', ascending=False)
print(f"\nTop 5:\n{importance_df.head().to_string(index=False)}")

joblib.dump(gb, '/home/claude/ocp_app/models/gradient_boosting.pkl')
joblib.dump(lr, '/home/claude/ocp_app/models/linear_regression.pkl')

metrics = {
    'gradient_boosting': {'r2': float(r2_gb), 'r2_full_dataset': float(r2_full),
                          'mae': float(mae_gb), 'rmse': float(rmse_gb),
                          'cv_r2_mean': float(cv_scores.mean())},
    'random_forest': {'r2': float(r2_rf)},
    'linear_regression': {'r2': float(r2_lr)},
    'features': features,
    'feature_importance': importance_df.to_dict('records'),
    'n_anomalies': int(df['anomalie'].sum()),
    'total_tonnage': float(df['tonnage'].sum()),
    'n_days': len(df)
}

with open('/home/claude/ocp_app/models/metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print("\n✅ Sauvegardé")
