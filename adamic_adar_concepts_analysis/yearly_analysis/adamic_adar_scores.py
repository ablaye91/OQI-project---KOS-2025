import csv 
import os
import networkx as nx
from networkx.algorithms.link_prediction import adamic_adar_index
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# ------- YEARLY AND LEVELS 4 TO 5 ------------------------

def generate_adamic_adar_scores_by_year():
    output_dir = "adamic_scores_by_year"
    os.makedirs(output_dir, exist_ok=True)

    # Lire les niveaux des concepts
    levels_df = pd.read_csv("concepts_levels.csv")
    levels_df['concept_id'] = levels_df['concept_id'].str.strip()  # au cas où il y a des espaces
    allowed_concepts = set(
        levels_df[levels_df['level'].isin([4, 5])]['concept_id'].apply(lambda x: x.split("/")[-1])
    )

    # Chargement des données
    df = pd.read_csv("quantum_subtree.csv")
    df = df.dropna(subset=['publication_year'])
    df['publication_year'] = df['publication_year'].astype(int)

    grouped = df.groupby('publication_year')['paper_id'].apply(list).sort_index()

    cumulative_articles = set()
    year_articles_cumulative = {}

    for year, paper_ids in grouped.items():
        cumulative_articles.update(paper_ids)
        year_articles_cumulative[year] = sorted(cumulative_articles)

    # Lecture complète du CSV en dictionnaire
    with open("quantum_subtree.csv", newline='', encoding='utf-8') as fichier_csv:
        lecteur = csv.DictReader(fichier_csv)
        article_data = {ligne['paper_id']: ligne for ligne in lecteur}

    for year, list_article in year_articles_cumulative.items():
        G = nx.Graph()
        print(f"Processing year: {year} with {len(list_article)} articles.")

        for article_id in list_article:
            article = article_data.get(article_id)
            if not article or not article.get("concepts"):
                continue

            try:
                concept_all = article["concepts"].split(";")
            except Exception as e:
                print(f"Erreur pour article {article_id}: {e}")
                continue

            concept_sliced = [
                i.split("|") for i in concept_all
                if "|" in i and i.split("|")[0].split("/")[-1] in allowed_concepts
            ]

            # Ajout des noeuds filtrés
            for item in concept_sliced:
                concept_link = item[0]
                concept_name = item[1]
                concept_id = concept_link.split('/')[-1]

                if concept_id not in G:
                    G.add_node(concept_id, Concept_name=concept_name, Concept_link=concept_link)

            # Connexion des concepts
            for i in range(len(concept_sliced)):
                for j in range(i + 1, len(concept_sliced)):
                    concept1 = concept_sliced[i][0].split('/')[-1]
                    concept2 = concept_sliced[j][0].split('/')[-1]
                    if not G.has_edge(concept1, concept2):
                        G.add_edge(concept1, concept2)

        # Calcul Adamic-Adar
        non_edges_list = list(nx.non_edges(G))
        print(f"Nombre de paires non connectées à évaluer pour {year}: {len(non_edges_list)}")

        adamic_preds = list(adamic_adar_index(G, tqdm(non_edges_list)))

        output_path = os.path.join(output_dir, f"{year}_adamic_scores.csv")
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Concept1_ID", "Concept1_Name",
                "Concept2_ID", "Concept2_Name",
                "AdamicAdarScore"
            ])
            for u, v, score in adamic_preds:
                name_u = G.nodes[u].get('Concept_name', 'Unknown')
                name_v = G.nodes[v].get('Concept_name', 'Unknown')
                writer.writerow([u, name_u, v, name_v, score])

    print("Fin de l’analyse par année.")



def visualiser_top_adamic_from_file(fichier_csv, top_n):
    adamic_preds = []

    # Lecture du fichier CSV
    with open(fichier_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        # On vérifie si les colonnes incluent les noms de concepts
        has_names = "Concept1_Name" in reader.fieldnames and "Concept2_Name" in reader.fieldnames

        for row in reader:
            concept1_id = row["Concept1_ID"] if "Concept1_ID" in row else row["Concept1"]
            concept2_id = row["Concept2_ID"] if "Concept2_ID" in row else row["Concept2"]
            score = float(row["AdamicAdarScore"])

            # Utilisation directe des noms si disponibles, sinon on garde les ID
            concept1_name = row.get("Concept1_Name", concept1_id)
            concept2_name = row.get("Concept2_Name", concept2_id)

            adamic_preds.append((concept1_name, concept2_name, score))

    # Top-N triés par score décroissant
    top_edges = sorted(adamic_preds, key=lambda x: x[2], reverse=True)[:top_n]

    # Création du graphe avec les noms directement
    G = nx.Graph()
    for u, v, score in top_edges:
        G.add_edge(u, v, weight=score)

    pos = nx.spring_layout(G, seed=42, k=0.9)
    plt.figure(figsize=(10, 8))

    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=1000)
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.7)
    nx.draw_networkx_labels(G, pos, font_size=10)

    edge_labels = {
        (u, v): f"{data['weight']:.2f}"
        for u, v, data in G.edges(data=True)
    }

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='gray', font_size=9)

    plt.title(f"Top {top_n} liens Adamic Adar depuis {fichier_csv}")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

# visualiser_top_adamic_from_file("adamic_scores_by_year/2021_adamic_scores.csv", 15)


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


def temporal_analysis():

    track_amount = None
    missing_data = []
    previous_concepts = set()
    tracked_pairs = set()
    pair_scores = {}
    first_year_track = 0
    years_graph_x = []
    top_concepts_scores=None

    for year in range(1965, 2024): 
        subfolder = f"adamic_scores_by_year"  
        filename = os.path.join(subfolder, f"{year}_adamic_scores.csv")

        if os.path.exists(filename):
            first_year_track += 1

            if first_year_track == 1:
                track_amount = 10
                top_concepts_scores = get_top_adamic_scores(filename, track_amount)
                print(f"Top concept scores : ", top_concepts_scores)

                tracked_pairs = {
                    tuple(sorted(((c1_id, c1_name), (c2_id, c2_name))))
                    for (c1_id, c1_name), (c2_id, c2_name), _ in top_concepts_scores
                }
                pair_scores = {pair: [] for pair in tracked_pairs}

            years_graph_x.append(str(year))
            current_scores = {}
            current_concepts = set()
            missing_tracked_concepts = []

            print(f"Traitement fichier {filename}")

            with open(filename, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    c1_id, c1_name = row["Concept1_ID"], row["Concept1_Name"]
                    c2_id, c2_name = row["Concept2_ID"], row["Concept2_Name"]
                    score = float(row["AdamicAdarScore"])
                    pair = tuple(sorted(((c1_id, c1_name), (c2_id, c2_name))))
                    current_scores[pair] = score
                    current_concepts.add(pair)

            for pair in tracked_pairs:
                if pair in current_scores:
                    pair_scores[pair].append(current_scores[pair])
                else:
                    pair_scores[pair].append(float("nan"))
                    missing_tracked_concepts.append(pair)

            if previous_concepts:
                common = current_concepts & previous_concepts
                added = current_concepts - previous_concepts
                removed = previous_concepts - current_concepts

                print(f"Comparaison avec l'année précédente :")
                print(f"   ➕ Nouveaux liens : {len(added)}")
                print(f"   ➖ Liens disparus : {len(removed)}")
                print(f"   ✅ Liens communs  : {len(common)}")

            previous_concepts = current_concepts
            print(f"Missing pairs in {year} : {missing_tracked_concepts}")

        else:
            missing_data.append(filename)

    # --- Sauvegarde du plot sans légende ---
    plt.figure(figsize=(12, 6))
    for pair, scores in pair_scores.items():
        (_, name1), (_, name2) = pair
        label = f"{name1} - {name2}"
        scores = np.array(scores, dtype=np.float32)
        plt.plot(years_graph_x, scores, marker='o', label=label)

    plt.xticks(rotation=45)
    plt.xlabel("Année")
    plt.ylabel("Adamic-Adar Score")
    plt.title(f"Évolution du score Adamic-Adar pour {track_amount} paires de concepts")
    plt.grid(True)
    plt.tight_layout(rect=[0, 0, 1, 1])  # plein espace sans légende

    output_dir = "plots"
    os.makedirs(output_dir, exist_ok=True)
    plot_file = os.path.join(output_dir, "adamic_adar_evolution_50_plot.png")
    # plt.savefig(plot_file, dpi=300)
    plt.show()
    plt.close()
    print(f"✅ Graphe enregistré dans {plot_file}")

    # --- Sauvegarde de la légende seule ---
    fig_legend = plt.figure(figsize=(6, max(2, len(pair_scores)*0.3)))
    ax = fig_legend.add_subplot(111)
    ax.axis('off')

    lines = []
    labels = []
    for pair in pair_scores:
        (_, name1), (_, name2) = pair
        label = f"{name1} - {name2}"
        line, = ax.plot([], [], marker='o')
        lines.append(line)
        labels.append(label)

    leg = ax.legend(lines, labels, loc='center')
    leg.get_frame().set_edgecolor('black')
    leg.get_frame().set_linewidth(0.5)

    plt.tight_layout()
    legend_file = os.path.join(output_dir, "adamic_adar_evolution_50_legend.png")
    # plt.savefig(legend_file, dpi=300)
    plt.close()
    print(f"✅ Légende enregistrée dans {legend_file}")

    # --- Affichage avec légende à droite ---
    plt.figure(figsize=(12, 6))
    for pair, scores in pair_scores.items():
        (_, name1), (_, name2) = pair
        label = f"{name1} - {name2}"
        scores = np.array(scores, dtype=np.float32)
        plt.plot(years_graph_x, scores, marker='o', label=label)

    plt.xticks(rotation=45)
    plt.xlabel("Année")
    plt.ylabel("Adamic-Adar Score")
    plt.title(f"Évolution du score Adamic-Adar pour {track_amount} paires de concepts")

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(True)
    plt.tight_layout(rect=[0, 0, 0.85, 1])

    # plt.show()

    print(f"Top concept scores : ", top_concepts_scores)