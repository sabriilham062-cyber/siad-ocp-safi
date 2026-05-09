"""Page 4 : Impact économique & environnemental — Green Supply Chain."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def show(df):
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0;color:white;">🌱 Impact économique & environnemental</h1>
        <p style="margin:0;opacity:0.9;">Green Supply Chain — Évaluation de la durabilité</p>
    </div>
    """, unsafe_allow_html=True)

    # === CHIFFRES CLÉS ===
    st.markdown("### 💎 Bilan annuel de l'optimisation")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Économies annuelles", "18.1M MAD", "+19.3%")
    with col2:
        st.metric("🌍 CO₂ évité", "958 t", "-16.1%", delta_color="inverse")
    with col3:
        st.metric("🚗 Équivalent voitures", "640", "retirées de la route")
    with col4:
        st.metric("🌳 Équivalent arbres", "43 800", "plantés/an")

    st.markdown("---")

    # === ONGLETS IMPACT ===
    tab1, tab2, tab3 = st.tabs(["💰 Impact économique", "🌍 Impact environnemental", "🎯 Stratégie ESG"])

    # === ONGLET 1 : ÉCONOMIQUE ===
    with tab1:
        st.markdown("### 💰 Analyse économique détaillée")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Comparaison scénarios")
            scenarios = pd.DataFrame({
                'Scénario': ['Actuel', 'Optimisé'],
                'Coût (MAD)': [df['cout_total_mad'].sum(),
                               df['cout_total_mad'].sum() * 0.807]
            })
            fig = px.bar(
                scenarios, x='Scénario', y='Coût (MAD)',
                color='Scénario',
                color_discrete_map={'Actuel': '#dc3545', 'Optimisé': '#28a745'},
                text='Coût (MAD)'
            )
            fig.update_traces(texttemplate='%{text:,.0f} MAD', textposition='outside')
            fig.update_layout(height=400, showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Évolution mensuelle des économies")
            df_monthly = df.groupby(df['date'].dt.to_period('M')).agg({
                'cout_total_mad': 'sum'
            }).reset_index()
            df_monthly['date'] = df_monthly['date'].dt.to_timestamp()
            df_monthly['economie'] = df_monthly['cout_total_mad'] * 0.193

            fig = px.area(
                df_monthly, x='date', y='economie',
                labels={'economie': 'Économies mensuelles (MAD)', 'date': ''},
                color_discrete_sequence=['#28a745']
            )
            fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 📊 Décomposition de l'économie réalisée")
        decomposition = pd.DataFrame({
            'Source': ['Réduction temps d\'attente', 'Optimisation affectations',
                      'Meilleur taux de remplissage', 'Réduction trajets à vide'],
            'Économie (MAD)': [5_400_000, 6_200_000, 3_500_000, 3_000_000]
        })
        fig = px.pie(
            decomposition, values='Économie (MAD)', names='Source',
            color_discrete_sequence=px.colors.sequential.Blues_r,
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div class="success-box">
            <strong>💡 ROI de la solution SIAD :</strong> les 18.1M MAD d'économies annuelles
            représentent un retour sur investissement immédiat compte tenu du coût de développement
            et de déploiement de la solution (estimé à <500k MAD).
        </div>
        """, unsafe_allow_html=True)

    # === ONGLET 2 : ENVIRONNEMENTAL ===
    with tab2:
        st.markdown("### 🌍 Empreinte carbone et durabilité")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Émissions de CO₂ : actuel vs optimisé")
            co2_actuel = df['co2_kg'].sum() / 1000
            co2_optimise = co2_actuel * (1 - 0.161)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=['Scénario actuel', 'Scénario optimisé'],
                y=[co2_actuel, co2_optimise],
                marker_color=['#dc3545', '#28a745'],
                text=[f'{co2_actuel:,.0f} t', f'{co2_optimise:,.0f} t'],
                textposition='outside'
            ))
            fig.update_layout(
                height=400, yaxis_title="CO₂ (tonnes)",
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Évolution mensuelle des émissions")
            df_monthly_co2 = df.groupby(df['date'].dt.to_period('M')).agg({
                'co2_kg': 'sum'
            }).reset_index()
            df_monthly_co2['date'] = df_monthly_co2['date'].dt.to_timestamp()
            df_monthly_co2['co2_t'] = df_monthly_co2['co2_kg'] / 1000
            df_monthly_co2['co2_optimise'] = df_monthly_co2['co2_t'] * 0.839

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_monthly_co2['date'], y=df_monthly_co2['co2_t'],
                name='Actuel', line=dict(color='#dc3545', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=df_monthly_co2['date'], y=df_monthly_co2['co2_optimise'],
                name='Optimisé', line=dict(color='#28a745', width=2),
                fill='tonexty', fillcolor='rgba(40,167,69,0.2)'
            ))
            fig.update_layout(
                height=400, yaxis_title="CO₂ (tonnes)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

        # === ÉQUIVALENCES PARLANTES ===
        st.markdown("### 🌳 Équivalences environnementales (1 an)")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("""
            <div class="metric-card" style="text-align:center;padding:1.5rem;">
                <div style="font-size:3rem;">🚗</div>
                <h3 style="margin:0.5rem 0;color:#1f3864;">640</h3>
                <p style="margin:0;color:#666;">voitures retirées<br>de la circulation</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="metric-card" style="text-align:center;padding:1.5rem;">
                <div style="font-size:3rem;">🌳</div>
                <h3 style="margin:0.5rem 0;color:#1f3864;">43 800</h3>
                <p style="margin:0;color:#666;">arbres plantés<br>et entretenus 10 ans</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="metric-card" style="text-align:center;padding:1.5rem;">
                <div style="font-size:3rem;">✈️</div>
                <h3 style="margin:0.5rem 0;color:#1f3864;">5 320</h3>
                <p style="margin:0;color:#666;">vols Casa-Paris<br>évités</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown("""
            <div class="metric-card" style="text-align:center;padding:1.5rem;">
                <div style="font-size:3rem;">🏠</div>
                <h3 style="margin:0.5rem 0;color:#1f3864;">192</h3>
                <p style="margin:0;color:#666;">foyers chauffés<br>pendant 1 an</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box" style="margin-top:1.5rem;">
            <strong>📐 Méthodologie de calcul :</strong> Conformément au GHG Protocol et aux facteurs d'émission ADEME,
            le calcul utilise un facteur d'émission ferroviaire industriel de 22 g CO₂/t.km, multiplié par la distance
            moyenne parcourue (35 km) et le tonnage transporté quotidien.
        </div>
        """, unsafe_allow_html=True)

    # === ONGLET 3 : STRATÉGIE ESG ===
    with tab3:
        st.markdown("### 🎯 Alignement avec la stratégie ESG du Groupe OCP")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("""
            #### 🌍 Objectifs de décarbonation OCP

            Le Groupe OCP s'est engagé dans une stratégie ambitieuse de **neutralité carbone à horizon 2040**.
            L'optimisation du transport ferroviaire interne contribue directement à cet objectif via :

            - ✅ **Réduction directe** des émissions opérationnelles (Scope 1)
            - ✅ **Optimisation énergétique** par réduction des trajets à vide
            - ✅ **Maintenance préventive** prolongeant la durée de vie du parc
            - ✅ **Reporting ESG** facilité par le suivi automatisé

            #### 🏆 Contribution aux ODD (Objectifs de Développement Durable)

            Cette démarche s'inscrit dans plusieurs ODD de l'ONU :
            - **ODD 9** : Industrie, innovation et infrastructure
            - **ODD 12** : Consommation et production durables
            - **ODD 13** : Mesures relatives à la lutte contre les changements climatiques
            """)

        with col2:
            st.markdown("""
            <div class="metric-card" style="padding:1.5rem;">
                <h4 style="color:#1f3864;margin-top:0;">📈 Indicateurs ESG</h4>
                <p><strong>Intensité carbone :</strong><br>
                <span style="color:#28a745;font-size:1.5rem;">↓ 16.1%</span></p>
                <p><strong>Efficacité énergétique :</strong><br>
                <span style="color:#28a745;font-size:1.5rem;">↑ 19.3%</span></p>
                <p><strong>Disponibilité du parc :</strong><br>
                <span style="color:#1f3864;font-size:1.5rem;">91.8%</span></p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("### 📜 Cadre normatif respecté")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            **🌐 GHG Protocol**
            Méthodologie internationale de comptabilité carbone, référence pour les Scopes 1, 2 et 3.
            """)
        with col2:
            st.markdown("""
            **🇫🇷 ADEME**
            Facteurs d'émission de l'Agence française de la transition écologique, référence européenne.
            """)
        with col3:
            st.markdown("""
            **🏛️ ISO 14064**
            Norme internationale pour la quantification et le reporting des émissions de gaz à effet de serre.
            """)
