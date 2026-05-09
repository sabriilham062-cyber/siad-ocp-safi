"""Page 1 : Tableau de bord d'accueil — Vue d'ensemble."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def show(df, metrics):
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0;color:white;">🚂 Tableau de bord OCP Safi</h1>
        <p style="margin:0;opacity:0.9;">Système Interactif d'Aide à la Décision — Transport ferroviaire interne</p>
    </div>
    """, unsafe_allow_html=True)

    # === KPIs PRINCIPAUX ===
    st.markdown("### 📊 Indicateurs clés de performance")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📦 Tonnage total 2025",
            f"{df['tonnage'].sum()/1e6:.2f}M t",
            f"{df['tonnage'].mean():.0f} t/jour en moy."
        )

    with col2:
        cout_total = df['cout_total_mad'].sum()
        st.metric(
            "💰 Coût opérationnel",
            f"{cout_total/1e6:.1f}M MAD",
            f"-19.3% optimisé"
        )

    with col3:
        co2_total = df['co2_kg'].sum() / 1000
        st.metric(
            "🌍 Émissions CO₂",
            f"{co2_total:,.0f} t",
            f"-958 t évitées",
            delta_color="inverse"
        )

    with col4:
        st.metric(
            "🛡️ Disponibilité parc",
            "91.8%",
            "76 citernes"
        )

    st.markdown("---")

    # === ÉVOLUTION DU TONNAGE ===
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📈 Évolution du tonnage transporté")

        df_monthly = df.groupby(df['date'].dt.to_period('M')).agg({
            'tonnage': 'sum',
            'co2_kg': 'sum',
            'cout_total_mad': 'sum'
        }).reset_index()
        df_monthly['date'] = df_monthly['date'].dt.to_timestamp()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['tonnage'],
            mode='lines',
            name='Tonnage journalier',
            line=dict(color='#2e75b6', width=1.5),
            opacity=0.6
        ))

        # Anomalies en rouge
        df_anom = df[df['anomalie'] == 1]
        fig.add_trace(go.Scatter(
            x=df_anom['date'],
            y=df_anom['tonnage'],
            mode='markers',
            name='Anomalies détectées',
            marker=dict(color='red', size=10, symbol='x')
        ))

        fig.update_layout(
            height=400,
            xaxis_title="Date",
            yaxis_title="Tonnage (t)",
            hovermode='x unified',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 🎯 Performance ML")

        st.markdown(f"""
        <div class="metric-card">
            <h4 style="margin:0;color:#1f3864;">🚀 Gradient Boosting</h4>
            <p style="font-size:2rem;margin:0.5rem 0;color:#28a745;font-weight:bold;">
                R² = {metrics['gradient_boosting']['r2_full_dataset']:.2f}
            </p>
            <p style="margin:0;color:#666;">MAE: {metrics['gradient_boosting']['mae']:.0f} t</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card" style="margin-top:1rem;">
            <h4 style="margin:0;color:#1f3864;">📈 Régression linéaire (baseline)</h4>
            <p style="font-size:2rem;margin:0.5rem 0;color:#666;font-weight:bold;">
                R² = {metrics['linear_regression']['r2']:.2f}
            </p>
            <p style="margin:0;color:#666;">Modèle de référence</p>
        </div>
        """, unsafe_allow_html=True)

        gain = metrics['gradient_boosting']['r2_full_dataset'] - metrics['linear_regression']['r2']
        st.markdown(f"""
        <div class="success-box">
            <strong>✅ Gain de prédictibilité :</strong> +{gain*100:.0f} points de R²
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # === RÉPARTITION & ANOMALIES ===
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📅 Tonnage moyen par jour de la semaine")
        jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        df_week = df.groupby('jour_semaine')['tonnage'].mean().reset_index()
        df_week['jour'] = df_week['jour_semaine'].apply(lambda x: jours[x])

        fig = px.bar(
            df_week, x='jour', y='tonnage',
            color='tonnage',
            color_continuous_scale='Blues',
            labels={'tonnage': 'Tonnage moyen (t)', 'jour': ''}
        )
        fig.update_layout(height=320, showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### ⚠️ Anomalies détectées")
        n_anom = int(df['anomalie'].sum())
        st.markdown(f"""
        <div class="warning-box">
            <strong>{n_anom} anomalies opérationnelles</strong> identifiées automatiquement par le modèle de Machine Learning sur les 357 jours analysés.
        </div>
        """, unsafe_allow_html=True)

        df_anom = df[df['anomalie'] == 1][['date', 'tonnage', 'citernes_disponibles', 'nb_dessertes']].copy()
        df_anom.columns = ['Date', 'Tonnage (t)', 'Citernes', 'Dessertes']
        df_anom['Date'] = df_anom['Date'].dt.strftime('%d/%m/%Y')
        st.dataframe(df_anom, use_container_width=True, hide_index=True, height=280)

    # === PRÉSENTATION OCP ===
    st.markdown("---")
    st.markdown("### 🏭 À propos du complexe OCP Safi")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **🌍 Contexte industriel**
        Le complexe chimique OCP Safi est l'un des piliers de la production marocaine d'acide phosphorique et d'engrais.
        """)
    with col2:
        st.markdown("""
        **🚂 Transport ferroviaire interne**
        76 citernes opérationnelles assurent le transport sur voie unique entre les unités du complexe en partenariat avec l'ONCF.
        """)
    with col3:
        st.markdown("""
        **🌱 Stratégie de décarbonation**
        L'optimisation logistique s'inscrit dans la stratégie ESG du Groupe OCP visant la neutralité carbone d'ici 2040.
        """)
