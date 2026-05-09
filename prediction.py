"""Page 2 : Prédiction du tonnage — Multi-horizons (jour, semaine, mois)."""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta


def predict_tonnage(model, date_obj, citernes=70, dessertes=12, temperature=20,
                    temps_chargement=45, taux_remplissage=0.92):
    """Effectue une prédiction pour une date donnée."""
    features = pd.DataFrame([{
        'jour_semaine': date_obj.weekday(),
        'mois': date_obj.month,
        'jour_mois': date_obj.day,
        'semaine_annee': date_obj.isocalendar()[1],
        'est_weekend': 1 if date_obj.weekday() >= 5 else 0,
        'citernes_disponibles': citernes,
        'nb_dessertes': dessertes,
        'temperature': temperature,
        'temps_chargement_moyen': temps_chargement,
        'taux_remplissage': taux_remplissage
    }])
    return float(model.predict(features)[0])


def show(df, model, metrics):
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0;color:white;">🔮 Prédiction du tonnage</h1>
        <p style="margin:0;opacity:0.9;">Modèle Gradient Boosting — Prévisions multi-horizons</p>
    </div>
    """, unsafe_allow_html=True)

    # Métriques du modèle en haut
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("R² (test)", f"{metrics['gradient_boosting']['r2']:.3f}")
    with col2:
        st.metric("R² (complet)", f"{metrics['gradient_boosting']['r2_full_dataset']:.3f}")
    with col3:
        st.metric("MAE", f"{metrics['gradient_boosting']['mae']:.0f} t")
    with col4:
        st.metric("RMSE", f"{metrics['gradient_boosting']['rmse']:.0f} t")

    st.markdown("---")

    # === ONGLETS HORIZONS ===
    tab1, tab2, tab3 = st.tabs(["📅 Demain (J+1)", "📆 Cette semaine (S+1)", "🗓️ Ce mois (M+1)"])

    # === ONGLET 1 : PRÉDICTION JOURNALIÈRE ===
    with tab1:
        st.markdown("### 🎯 Prédiction pour une date précise")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("**Paramètres opérationnels**")
            target_date = st.date_input(
                "Date cible",
                value=datetime(2026, 5, 12),
                min_value=datetime(2026, 1, 1),
                max_value=datetime(2027, 12, 31)
            )
            citernes = st.slider("Citernes disponibles", 50, 76, 70)
            dessertes = st.slider("Nombre de dessertes prévues", 5, 18, 12)
            temperature = st.slider("Température prévue (°C)", 5, 40, 22)
            temps_chargement = st.slider("Temps de chargement moyen (min)", 30, 60, 45)
            taux_remplissage = st.slider("Taux de remplissage (%)", 80, 100, 92) / 100

            predict_btn = st.button("🚀 Lancer la prédiction", type="primary", use_container_width=True)

        with col2:
            if predict_btn or True:  # Toujours actif pour démo
                date_obj = pd.Timestamp(target_date)
                pred = predict_tonnage(model, date_obj, citernes, dessertes,
                                       temperature, temps_chargement, taux_remplissage)

                # Calcul intervalle de confiance (simplifié)
                rmse = metrics['gradient_boosting']['rmse']
                ic_low = pred - 1.96 * rmse
                ic_high = pred + 1.96 * rmse

                # Détection d'anomalie
                tonnage_moyen = df['tonnage'].mean()
                tonnage_std = df['tonnage'].std()
                z_score = abs(pred - tonnage_moyen) / tonnage_std
                est_anomalie = z_score > 2.5

                st.markdown(f"""
                <div class="metric-card" style="text-align:center;padding:2rem;">
                    <h4 style="margin:0;color:#666;">Tonnage prévu</h4>
                    <p style="font-size:3.5rem;margin:0.5rem 0;color:#1f3864;font-weight:bold;">
                        {pred:,.0f} <span style="font-size:1.5rem;color:#666;">tonnes</span>
                    </p>
                    <p style="color:#666;margin:0;">
                        Intervalle 95% : <strong>{ic_low:,.0f}</strong> – <strong>{ic_high:,.0f}</strong> t
                    </p>
                </div>
                """, unsafe_allow_html=True)

                if est_anomalie:
                    st.markdown(f"""
                    <div class="warning-box">
                        <strong>⚠️ Prédiction anormale détectée</strong><br>
                        Z-score = {z_score:.2f} (seuil : 2.5). Vérifiez les paramètres saisis.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="success-box">
                        <strong>✅ Prédiction dans la plage normale</strong> (Z-score = {z_score:.2f})
                    </div>
                    """, unsafe_allow_html=True)

                # Comparaison avec moyenne historique
                ecart = ((pred - tonnage_moyen) / tonnage_moyen) * 100
                st.markdown(f"""
                <div class="info-box">
                    📊 <strong>Vs. moyenne historique :</strong> {ecart:+.1f}%
                    ({pred - tonnage_moyen:+,.0f} t)
                </div>
                """, unsafe_allow_html=True)

                # Recommandations automatiques
                st.markdown("**💡 Recommandations automatiques**")
                jour_nom = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'][date_obj.weekday()]

                recos = []
                if pred > tonnage_moyen * 1.15:
                    recos.append(f"📈 Journée chargée prévue ({jour_nom}) : prévoir des citernes supplémentaires")
                if citernes < 65:
                    recos.append(f"⚠️ Parc réduit : programmer la maintenance en dehors des pics")
                if taux_remplissage < 0.88:
                    recos.append(f"🎯 Taux de remplissage faible : optimiser le chargement")
                if temps_chargement > 50:
                    recos.append(f"⏱️ Temps de chargement élevé : revoir les procédures")
                if not recos:
                    recos.append("✅ Conditions opérationnelles optimales — aucune action particulière requise")

                for r in recos:
                    st.markdown(f"- {r}")

    # === ONGLET 2 : PRÉDICTION HEBDOMADAIRE ===
    with tab2:
        st.markdown("### 📆 Prévision sur 7 jours")

        start_week = st.date_input(
            "Début de la semaine",
            value=datetime(2026, 5, 11),
            key="start_week"
        )

        # Génération des prédictions pour 7 jours
        predictions_week = []
        for i in range(7):
            d = pd.Timestamp(start_week) + timedelta(days=i)
            pred = predict_tonnage(model, d)
            predictions_week.append({
                'date': d,
                'jour': ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'][d.weekday()],
                'tonnage_prevu': pred
            })

        df_week = pd.DataFrame(predictions_week)
        df_week['date_label'] = df_week['date'].dt.strftime('%d/%m') + ' (' + df_week['jour'] + ')'

        col1, col2 = st.columns([2, 1])

        with col1:
            fig = px.bar(
                df_week, x='date_label', y='tonnage_prevu',
                color='tonnage_prevu', color_continuous_scale='Blues',
                labels={'tonnage_prevu': 'Tonnage prévu (t)', 'date_label': ''}
            )
            fig.add_hline(y=df['tonnage'].mean(), line_dash="dash",
                         line_color="red", annotation_text="Moyenne historique")
            fig.update_layout(height=400, showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            total_week = df_week['tonnage_prevu'].sum()
            avg_week = df_week['tonnage_prevu'].mean()
            peak_day = df_week.loc[df_week['tonnage_prevu'].idxmax()]

            st.metric("📦 Total semaine", f"{total_week:,.0f} t")
            st.metric("📊 Moyenne / jour", f"{avg_week:,.0f} t")
            st.metric("📈 Pic prévu", f"{peak_day['date_label']}", f"{peak_day['tonnage_prevu']:,.0f} t")

            # Citernes nécessaires
            citernes_needed = int(np.ceil(peak_day['tonnage_prevu'] / 80))
            st.markdown(f"""
            <div class="info-box">
                💡 <strong>Recommandation :</strong> prévoir au moins <strong>{citernes_needed} citernes</strong> opérationnelles pour le jour de pic.
            </div>
            """, unsafe_allow_html=True)

    # === ONGLET 3 : PRÉDICTION MENSUELLE ===
    with tab3:
        st.markdown("### 🗓️ Prévision sur 30 jours")

        start_month = st.date_input(
            "Début de la période",
            value=datetime(2026, 6, 1),
            key="start_month"
        )

        predictions_month = []
        for i in range(30):
            d = pd.Timestamp(start_month) + timedelta(days=i)
            pred = predict_tonnage(model, d)
            predictions_month.append({'date': d, 'tonnage_prevu': pred})

        df_month = pd.DataFrame(predictions_month)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 Tonnage prévu", f"{df_month['tonnage_prevu'].sum()/1000:,.1f} kt")
        with col2:
            st.metric("📊 Moyenne / jour", f"{df_month['tonnage_prevu'].mean():,.0f} t")
        with col3:
            cout_prevu = df_month['tonnage_prevu'].sum() * 18.5
            st.metric("💰 Coût estimé", f"{cout_prevu/1e6:.2f}M MAD")
        with col4:
            co2_prevu = df_month['tonnage_prevu'].sum() * 22 * 35 / 1e6
            st.metric("🌍 CO₂ estimé", f"{co2_prevu:.1f} t")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_month['date'], y=df_month['tonnage_prevu'],
            mode='lines+markers', name='Prévision',
            line=dict(color='#2e75b6', width=2),
            fill='tozeroy', fillcolor='rgba(46,117,182,0.1)'
        ))
        fig.add_hline(y=df['tonnage'].mean(), line_dash="dash",
                     line_color="red", annotation_text="Moyenne historique 2025")
        fig.update_layout(
            height=400, xaxis_title="Date", yaxis_title="Tonnage (t)",
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Résumé textuel
        ecart_pct = ((df_month['tonnage_prevu'].sum() - df['tonnage'].mean() * 30) / (df['tonnage'].mean() * 30)) * 100
        st.markdown(f"""
        <div class="info-box">
            📊 <strong>Synthèse mensuelle :</strong> Le tonnage prévu sur 30 jours est de
            <strong>{df_month['tonnage_prevu'].sum()/1000:,.1f} kt</strong>, soit <strong>{ecart_pct:+.1f}%</strong>
            par rapport à la moyenne historique. Cette prévision permet de planifier les ressources
            (citernes, créneaux, maintenance) en amont.
        </div>
        """, unsafe_allow_html=True)
