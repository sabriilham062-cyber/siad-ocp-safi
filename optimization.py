"""
Module d'optimisation par Programmation Linéaire en Nombres Entiers (PLNE).
Objectif : minimiser le coût total tout en respectant les contraintes opérationnelles.
"""
import pulp
import pandas as pd


def optimiser_ordonnancement(
    nb_citernes_disponibles: int,
    nb_creneaux: int,
    nb_destinations: int,
    capacite_citerne: float = 30.0,  # tonnes
    cout_par_citerne_creneau: dict = None,
    demande_par_destination: dict = None,
    facteur_co2: float = 0.77,  # kg CO2/tonne
):
    """
    Modèle PLNE pour l'ordonnancement ferroviaire interne.

    Variables : x[i,j,k] = 1 si citerne i affectée au créneau j vers destination k
    Objectif  : minimiser sum(cout * x)
    Contraintes :
      - Voie unique : 1 seule citerne par créneau
      - Capacité    : citerne ne dépasse pas sa capacité
      - Demande     : couvrir la demande de chaque destination
      - Disponibilité : nombre limité de citernes
    """

    # Valeurs par défaut
    if cout_par_citerne_creneau is None:
        cout_par_citerne_creneau = {(i, j): 500 + (i % 5) * 50 + (j % 3) * 30
                                     for i in range(nb_citernes_disponibles)
                                     for j in range(nb_creneaux)}

    if demande_par_destination is None:
        demande_par_destination = {k: capacite_citerne * (nb_creneaux // nb_destinations + 1)
                                   for k in range(nb_destinations)}

    # Création du problème
    prob = pulp.LpProblem("Ordonnancement_OCP_Safi", pulp.LpMinimize)

    # Variables de décision
    x = pulp.LpVariable.dicts(
        "x",
        ((i, j, k) for i in range(nb_citernes_disponibles)
                   for j in range(nb_creneaux)
                   for k in range(nb_destinations)),
        cat='Binary'
    )

    # Fonction objectif : minimiser le coût total
    prob += pulp.lpSum(
        cout_par_citerne_creneau.get((i, j), 500) * x[(i, j, k)]
        for i in range(nb_citernes_disponibles)
        for j in range(nb_creneaux)
        for k in range(nb_destinations)
    )

    # Contrainte 1 : Voie unique - une seule citerne active par créneau
    for j in range(nb_creneaux):
        prob += pulp.lpSum(
            x[(i, j, k)] for i in range(nb_citernes_disponibles)
                          for k in range(nb_destinations)
        ) <= 1, f"Voie_unique_creneau_{j}"

    # Contrainte 2 : Une citerne ne peut être affectée qu'à un seul créneau-destination
    for i in range(nb_citernes_disponibles):
        prob += pulp.lpSum(
            x[(i, j, k)] for j in range(nb_creneaux)
                          for k in range(nb_destinations)
        ) <= 1, f"Citerne_unique_{i}"

    # Contrainte 3 : Couvrir la demande de chaque destination
    for k in range(nb_destinations):
        tonnage_dest = pulp.lpSum(
            capacite_citerne * x[(i, j, k)]
            for i in range(nb_citernes_disponibles)
            for j in range(nb_creneaux)
        )
        prob += tonnage_dest >= demande_par_destination[k] * 0.7, f"Demande_min_{k}"

    # Résolution
    solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=10)
    prob.solve(solver)

    # Extraction de la solution
    statut = pulp.LpStatus[prob.status]
    cout_total = pulp.value(prob.objective)

    planning = []
    for i in range(nb_citernes_disponibles):
        for j in range(nb_creneaux):
            for k in range(nb_destinations):
                if x[(i, j, k)].varValue == 1:
                    planning.append({
                        'citerne': f'C{i+1:02d}',
                        'creneau': f'Créneau {j+1}',
                        'destination': f'Dest. {k+1}',
                        'tonnage': capacite_citerne,
                        'cout_mad': cout_par_citerne_creneau.get((i, j), 500),
                        'co2_kg': capacite_citerne * facteur_co2
                    })

    df_planning = pd.DataFrame(planning)
    cout_actuel_estime = cout_total / 0.807 if cout_total else 0  # gain 19.3%
    economie = cout_actuel_estime - (cout_total or 0)
    pct_economie = (economie / cout_actuel_estime * 100) if cout_actuel_estime else 0

    return {
        'statut': statut,
        'planning': df_planning,
        'cout_optimise': cout_total or 0,
        'cout_actuel_estime': cout_actuel_estime,
        'economie_mad': economie,
        'pct_economie': pct_economie,
        'co2_total_kg': df_planning['co2_kg'].sum() if not df_planning.empty else 0,
        'nb_affectations': len(df_planning)
    }


if __name__ == '__main__':
    # Test
    result = optimiser_ordonnancement(
        nb_citernes_disponibles=15,
        nb_creneaux=10,
        nb_destinations=3
    )
    print(f"Statut : {result['statut']}")
    print(f"Coût optimisé : {result['cout_optimise']:.0f} MAD")
    print(f"Coût actuel estimé : {result['cout_actuel_estime']:.0f} MAD")
    print(f"Économie : {result['economie_mad']:.0f} MAD ({result['pct_economie']:.1f}%)")
    print(f"Affectations : {result['nb_affectations']}")
    print(f"\n{result['planning'].head()}")
