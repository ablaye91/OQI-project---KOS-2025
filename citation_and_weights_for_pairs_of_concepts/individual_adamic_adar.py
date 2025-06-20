import os
import matplotlib.pyplot as plt
import numpy as np
import csv

def track_pair_evolution_by_ids(concept1_id, concept2_id):
    """
    Affiche l'évolution du score Adamic-Adar dans le temps pour une paire de concepts identifiés par leurs IDs.
    
    concept1_id : str
    concept2_id : str
    """
    years = []
    scores = []
    missing_data = []

    for year in range(1965, 2024):
        filename = f"adamic_scores_by_year/{year}_adamic_scores.csv"
        years.append(str(year))

        if not os.path.exists(filename):
            scores.append(float("nan"))
            missing_data.append(year)
            continue

        found = False
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                c1_id, c1_name = row["Concept1_ID"], row["Concept1_Name"]
                c2_id, c2_name = row["Concept2_ID"], row["Concept2_Name"]

                pair_match = sorted([c1_id, c2_id]) == sorted([concept1_id, concept2_id])
                if pair_match:
                    scores.append(float(row["AdamicAdarScore"]))
                    found = True
                    break

        if not found:
            scores.append(float("nan"))

    # Affichage du graphe
    plt.figure(figsize=(10, 5))
    plt.plot(years, scores, marker='o', linestyle='-', color='blue', label=f"{concept1_id} - {concept2_id}")
    plt.xticks(rotation=45)
    plt.xlabel("Année")
    plt.ylabel("Adamic-Adar Score")
    plt.title(f"Évolution du score Adamic-Adar : {concept1_id} - {concept2_id}")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.show()

    if missing_data:
        print("📂 Fichiers manquants pour les années :", missing_data)

track_pair_evolution_by_ids('C206040425','C5320026')
track_pair_evolution_by_ids('C78203541','C186468114')
track_pair_evolution_by_ids('C118704821','C91717678')
track_pair_evolution_by_ids('C2778361524','C95013731')
track_pair_evolution_by_ids('C104434177','C190463098')
track_pair_evolution_by_ids('C104434177','C203103908')
track_pair_evolution_by_ids('C124148022','C51003876')
track_pair_evolution_by_ids('C124148022','C2779094486')
track_pair_evolution_by_ids('C124148022','C190463098')
track_pair_evolution_by_ids('C144901912','C190463098')
track_pair_evolution_by_ids('C139356082','C190463098')
track_pair_evolution_by_ids('C51003876','C5320026')
track_pair_evolution_by_ids('C51003876','C11255438')
track_pair_evolution_by_ids('C51003876','C89143813')
track_pair_evolution_by_ids('C51003876','C91717678')
track_pair_evolution_by_ids('C59500034','C186468114')
track_pair_evolution_by_ids('C58849907','C190463098')
track_pair_evolution_by_ids('C22984246','C203103908')
track_pair_evolution_by_ids('C5320026','C95013731')
track_pair_evolution_by_ids('C2779094486','C186468114')
track_pair_evolution_by_ids('C186468114','C138622882')
track_pair_evolution_by_ids('C186468114','C192122513')
track_pair_evolution_by_ids('C186468114','C11255438')
track_pair_evolution_by_ids('C186468114','C62641251')
track_pair_evolution_by_ids('C186468114','C140058369')
track_pair_evolution_by_ids('C11255438','C190463098')
track_pair_evolution_by_ids('C89143813','C91717678')
track_pair_evolution_by_ids('C161166931','C190463098')