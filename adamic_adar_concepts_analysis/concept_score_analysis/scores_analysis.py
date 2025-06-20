import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from collections import defaultdict
import pandas as pd


def get_top_adamic_scores(csv_file, top_n):
    scores = []

    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            concept1_id = row["Concept1_ID"]
            concept2_id = row["Concept2_ID"]
            concept1_name = row["Concept1_Name"]
            concept2_name = row["Concept2_Name"]
            score = float(row["AdamicAdarScore"])
            scores.append(((concept1_id, concept1_name), (concept2_id, concept2_name), score))

    top_scores = sorted(scores, key=lambda x: x[2], reverse=True)[:top_n]
    return top_scores


def plot_individual_concept_scores(top_year=1965, top_n=10):



    # Étape 1 : Récupérer les concepts à suivre
    top_scores = get_top_adamic_scores(f"adamic_scores_by_year/{top_year}_adamic_scores.csv", top_n)
    concepts_to_track = set()
    concept_id_to_name = {}

    for (c1_id, c1_name), (c2_id, c2_name), _ in top_scores:
        concepts_to_track.add(c1_id)
        concepts_to_track.add(c2_id)
        concept_id_to_name[c1_id] = c1_name
        concept_id_to_name[c2_id] = c2_name

    print(f"Tracking {len(concepts_to_track)} unique concepts from top {top_n} pairs of {top_year}")

    # Étape 2 : Regrouper les scores par concept et par année
    concept_scores_by_year = defaultdict(lambda: defaultdict(list))

    with open("quantum_subtree.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = row.get("publication_year")
            if not year or not year.isdigit():
                continue
            year = int(year)

            concepts_str = row.get("concepts", "")
            for concept_entry in concepts_str.split(";"):
                if "|" not in concept_entry:
                    continue
                try:
                    concept_uri, name, score_str = concept_entry.strip().split("|")
                    concept_id = concept_uri.split("/")[-1]
                    score = float(score_str)
                except Exception:
                    continue

                if concept_id in concepts_to_track:
                    concept_scores_by_year[concept_id][year].append(score)

    # Étape 3 : Calcul des moyennes par année
    concept_avg_scores = {
        concept_id: {
            year: np.nanmean(scores) if scores else np.nan
            for year, scores in year_scores.items()
        }
        for concept_id, year_scores in concept_scores_by_year.items()
    }

    # Étape 4 : Tracer les courbes
    all_years = sorted({year for scores in concept_avg_scores.values() for year in scores})
    all_years_str = [str(y) for y in all_years]

    plt.figure(figsize=(14, 7))
    colors = cm.get_cmap('tab20', len(concept_avg_scores))  # Une couleur unique par concept

    for idx, (concept_id, scores_by_year) in enumerate(concept_avg_scores.items()):
        scores = [scores_by_year.get(y, np.nan) for y in all_years]
        masked_scores = np.ma.masked_invalid(scores)  # Masquer les NaN pour éviter les discontinuités visuelles
        plt.plot(all_years_str, masked_scores, marker='o', label=concept_id_to_name.get(concept_id, concept_id), color=colors(idx))

    plt.xticks(rotation=45)
    plt.xlabel("Année")
    plt.ylabel("Score moyen du concept dans les articles")
    plt.title(f"Évolution des scores individuels des concepts (top {top_n} paires de {top_year})")
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# plot_individual_concept_scores(top_year=1965, top_n=10)



import os
import matplotlib.pyplot as plt
import numpy as np
import csv
from collections import defaultdict
import matplotlib.cm as cm
import re

def sanitize_filename(name):
    return re.sub(r'[^\w\-_. ]', '_', name).strip()

def plot_and_save_concept_score_evolution(top_year=1965, top_n=10, output_dir="concept_graphs"):
    # Étape 1 : Récupérer les concepts à suivre
    top_scores = get_top_adamic_scores(f"adamic_scores_by_year/{top_year}_adamic_scores.csv", top_n)
    concepts_to_track = set()
    concept_id_to_name = {}

    for (c1_id, c1_name), (c2_id, c2_name), _ in top_scores:
        concepts_to_track.add(c1_id)
        concepts_to_track.add(c2_id)
        concept_id_to_name[c1_id] = c1_name
        concept_id_to_name[c2_id] = c2_name

    print(f"Tracking {len(concepts_to_track)} unique concepts from top {top_n} pairs of {top_year}")

    # Étape 2 : Récupérer les scores annuels
    concept_scores_by_year = defaultdict(lambda: defaultdict(list))

    with open("quantum_subtree.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = row.get("publication_year")
            if not year or not year.isdigit():
                continue
            year = int(year)

            concepts_str = row.get("concepts", "")
            for concept_entry in concepts_str.split(";"):
                if "|" not in concept_entry:
                    continue
                try:
                    concept_uri, name, score_str = concept_entry.strip().split("|")
                    concept_id = concept_uri.split("/")[-1]
                    score = float(score_str)
                except Exception:
                    continue

                if concept_id in concepts_to_track:
                    concept_scores_by_year[concept_id][year].append(score)

    # Étape 3 : Calcul des moyennes
    concept_avg_scores = {
        concept_id: {
            year: np.nanmean(scores) if scores else np.nan
            for year, scores in year_scores.items()
        }
        for concept_id, year_scores in concept_scores_by_year.items()
    }

    # Étape 4 : Création du dossier de sortie
    os.makedirs(output_dir, exist_ok=True)

    # Étape 5 : Tracer et sauvegarder chaque courbe
    all_years = sorted({year for scores in concept_avg_scores.values() for year in scores})
    all_years_str = [str(y) for y in all_years]

    for concept_id, scores_by_year in concept_avg_scores.items():
        # Créer une série pandas avec les années comme index
        year_index = pd.Index(all_years, name="year")
        series = pd.Series({year: scores_by_year.get(year, np.nan) for year in all_years}, index=year_index)

        # Interpolation linéaire sur les années manquantes
        interpolated_series = series.interpolate(method='linear', limit_direction='both')

        scores = interpolated_series.tolist()

        plt.figure(figsize=(10, 5))
        plt.plot(all_years_str, scores, marker='o', color='tab:blue')

        xtick_years = [str(y) for y in all_years if y % 5 == 0]
        xtick_positions = [i for i, y in enumerate(all_years) if y % 5 == 0]
        plt.xticks(ticks=xtick_positions, labels=xtick_years, rotation=45)
        
        plt.title(f"Évolution du score pour le concept : {concept_id_to_name.get(concept_id, concept_id)}")
        plt.xlabel("Année")
        plt.ylabel("Score moyen dans les articles")
        plt.grid(True)
        plt.tight_layout()

        concept_name = concept_id_to_name.get(concept_id, concept_id)
        filename = sanitize_filename(f"{concept_name}.png")
        save_path = os.path.join(output_dir, filename)
        plt.savefig(save_path)
        plt.close()

        print(f"Graphique sauvegardé : {save_path}")

plot_and_save_concept_score_evolution(top_year=1965, top_n=10)
