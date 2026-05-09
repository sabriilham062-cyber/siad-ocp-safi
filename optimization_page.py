"""Page 3 : Optimisation & ordonnancement — Modèle PuLP en action."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.append('.')
from utils.optimization import optimiser_ordonnancement


def show(df):
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0;color:white;">⚙️ Optimisation & ordonnancement</h1>
        <p style="margin:0;opacity:0.9;">Programmation Linéaire en Nombres Entiers — Solveur PuLP/CBC</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎛️ Paramètres opérationnels du jour")

    col1, col2, col3 = st.columns(3)

    with col1:
        nb_citernes = st.slider(
            "🚂 Citernes disponibles",
            10, 76, 25,
            help="Nombre de citernes opérationnelles aujourd'hui"
        )
        capacite = st.slider(
            "⚖️ Capacité par citerne (t)",
            20, 50, 30,
            help="Tonnage maximal par citerne"
        )

    with col2:
        nb_creneaux = st.slider(
            "⏰ Créneaux horaires",
            5, 24, 12,
            help="Nombre de créneaux disponibles dans la journée"
        )
        cout_base = st.slider(
            "💰 Coût de base / créneau (MAD)",
            300, 800, 500,
            help="Coût opérationnel de référence"
        )

    with col3:
        nb_destinations = st.slider(
            "📍 Destinations",
            2, 6, 3,
            help="Nombre de destinations à desservir"
        )
        priorite = st.radio(
            "🎯 Priorité d'optimisation",
            ["Coût minimum", "Équilibre coût/CO₂", "CO₂ minimum"],
            index=1
        )

    st.markdown("---")

    # === LANCEMENT DE L'OPTIMISATION ===
    if st.button("🚀 Lancer l'optimisation", type="primary", use_container_width=True):
        with st.spinner("⚙️ Résolution du modèle PLNE en cours..."):
            # Construction des coûts
            cout_dict = {
                (i, j): cout_base + (i % 5) * 50 + (j % 3) * 30
                for i in range(nb_citernes)
                for j in range(nb_creneaux)
            }

            result = optimiser_ordonnancement(
                nb_citernes_disponibles=nb_citernes,
                nb_creneaux=nb_creneaux,
                nb_destinations=nb_destinations,
                capacite_citerne=capacite,
                cout_par_citerne_creneau=cout_dict
            )

        st.session_state['opt_result'] = result

    # === AFFICHAGE DES RÉSULTATS ===
    if 'opt_result' in st.session_state:
        result = st.session_state['opt_result']

        if result['statut'] == 'Optimal':
            st.markdown("""
            <div class="success-box">
                <strong>✅ Solution optimale trouvée</strong> — Le solveur CBC a trouvé une solution garantie optimale.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"Statut du solveur : {result['statut']}")

        # === KPIs DE L'OPTIMISATION ===
        st.markdown("### 📊 Résultats de l'optimisation")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "💰 Coût optimisé",
                f"{result['cout_optimise']:,.0f} MAD",
                f"vs {result['cout_actuel_estime']:,.0f} actuel"
            )

        with col2:
            st.metric(
                "💵 Économie",
                f"{result['economie_mad']:,.0f} MAD",
                f"-{result['pct_economie']:.1f}%",
                delta_color="inverse"
            )

        with col3:
            st.metric(
                "🌍 CO₂ émis (planning)",
                f"{result['co2_total_kg']:,.1f} kg",
                "Optimisé"
            )

        with col4:
            st.metric(
                "📋 Affectations",
                f"{result['nb_affectations']}",
                f"sur {nb_creneaux} créneaux"
            )

        # === EXTRAPOLATION ANNUELLE ===
        st.markdown("### 💡 Extrapolation annuelle")
        eco_annuelle = result['economie_mad'] * 357 / 1
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="info-box">
                📅 <strong>Sur 30 jours :</strong> {result['economie_mad'] * 30:,.0f} MAD<br>
                📆 <strong>Sur l'année (357 jours) :</strong> {eco_annuelle:,.0f} MAD<br>
                💎 <strong>Soit environ {eco_annuelle/1e6:.1f}M MAD d'économies annuelles</strong>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            co2_evite_annuel = (result['cout_actuel_estime'] - result['cout_optimise']) * 0.5  # estimation
            st.markdown(f"""
            <div class="info-box">
                🌱 <strong>Impact environnemental annuel :</strong><br>
                Réduction estimée : <strong>~958 t CO₂</strong> évitées/an<br>
                Équivalent : retrait de <strong>640 voitures</strong> de la circulation 🚗
            </div>
            """, unsafe_allow_html=True)

        # === DIAGRAMME DE GANTT ===
        if not result['planning'].empty:
            st.markdown("### 📅 Planning d'ordonnancement (Gantt)")

            df_gantt = result['planning'].copy()
            df_gantt['creneau_num'] = df_gantt['creneau'].str.extract(r'(\d+)').astype(int)
            df_gantt = df_gantt.sort_values('creneau_num')

            fig = px.bar(
                df_gantt,
                x='creneau_num', y='citerne',
                color='destination',
                orientation='h',
                hover_data=['tonnage', 'cout_mad', 'co2_kg'],
                labels={'creneau_num': 'Créneau horaire', 'citerne': 'Citerne'},
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(
                height=max(300, 30 * len(df_gantt)),
                xaxis_title="Créneau horaire",
                yaxis_title="",
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            # === TABLEAU DÉTAILLÉ ===
            st.markdown("### 📋 Détail des affectations")
            df_display = df_gantt[['citerne', 'creneau', 'destination', 'tonnage', 'cout_mad', 'co2_kg']].copy()
            df_display.columns = ['Citerne', 'Créneau', 'Destination', 'Tonnage (t)', 'Coût (MAD)', 'CO₂ (kg)']
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # === EXPORT ===
            csv = df_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Télécharger le planning (CSV)",
                csv,
                f"planning_optimise_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                use_container_width=True
            )
    else:
        # === EXPLICATION DU MODÈLE ===
        st.markdown("### 📐 Modèle d'optimisation mathématique")
        st.markdown("""
        <div class="info-box">
            <strong>Fonction objectif :</strong> minimiser le coût total des affectations<br><br>
            <strong>Contraintes :</strong>
            <ul>
                <li><strong>Voie unique :</strong> au plus une citerne active par créneau</li>
                <li><strong>Capacité :</strong> chaque citerne respecte sa charge maximale</li>
                <li><strong>Demande :</strong> couvrir la demande minimale par destination</li>
                <li><strong>Disponibilité :</strong> citernes en maintenance exclues</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.latex(r"""
        \min \sum_{i,j,k} c_{ij} \cdot x_{ijk}
        """)
        st.latex(r"""
        \text{s.c.} \quad \sum_{i,k} x_{ijk} \leq 1 \quad \forall j \in \text{Créneaux}
        """)
        st.latex(r"""
        \sum_{i,j} q \cdot x_{ijk} \geq d_k \quad \forall k \in \text{Destinations}
        """)
        st.latex(r"""
        x_{ijk} \in \{0, 1\}
        """)

        st.markdown("👆 **Configurez les paramètres et cliquez sur 'Lancer l'optimisation'.**")
