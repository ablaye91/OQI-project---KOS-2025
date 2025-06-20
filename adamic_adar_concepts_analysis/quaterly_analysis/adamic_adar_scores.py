import csv 
import os
import requests
import networkx as nx
from networkx.algorithms.link_prediction import adamic_adar_index
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



def get_season_label(date):

    year = date.year
    month = date.month
    if month in [1, 2, 3]:
        season = 'winter'
    elif month in [4, 5, 6]:
        season = 'spring'
    elif month in [7, 8, 9]:
        season = 'summer'
    else:
        season = 'fall'
    return f"{season}_{year}"



def generate_adamic_adar_scores_levels(levels):

    output_dir = f"adamic_scores_levels_{'_'.join(levels)}"
    os.makedirs(output_dir, exist_ok=True)

    allowed_concepts = set()
    with open('concepts_levels.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for ligne in reader:
            if str(ligne["level"]) in levels:
                concept_id = ligne["concept_id"].split("/")[-1]
                allowed_concepts.add(concept_id)

    # Lecture du dataset principal
    df = pd.read_csv("quantum_networks_log_papers.csv")
    df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce')
    df = df.dropna(subset=['publication_date'])
    df['season_label'] = df['publication_date'].apply(get_season_label)

    season_order = {'winter': 1, 'spring': 2, 'summer': 3, 'fall': 4}
    df['season'] = df['season_label'].str.extract(r'(\w+)_\d+')[0]
    df['year'] = df['season_label'].str.extract(r'_(\d+)')[0].astype(int)
    df['season_rank'] = df['season'].map(season_order)
    grouped = df.groupby(['year', 'season_rank', 'season_label'])['paper_id'].apply(list)
    grouped = grouped.sort_index()

    cumulative_articles = set()
    season_articles_cumulative = {}

    for (_, _, label), paper_ids in grouped.items():
        cumulative_articles.update(paper_ids)
        season_articles_cumulative[label] = sorted(cumulative_articles)

    # Charger les données d’articles
    with open("quantum_networks_log_papers.csv", newline='', encoding='utf-8') as fichier_csv:
        lecteur = csv.DictReader(fichier_csv)
        article_data = {ligne['paper_id']: ligne for ligne in lecteur}

    for season, list_article in list(season_articles_cumulative.items()):
        G = nx.Graph()

        for article_id in list_article:
            article = article_data.get(article_id)
            if not article:
                continue

            concept_all = article.get("concepts", "").split(";")
            concept_sliced = [i.split("|") for i in concept_all if len(i.split("|")) == 2]

            # Appliquer le filtre de niveau ici
            concept_ids_filtered = [
                item[0].split('/')[-1]
                for item in concept_sliced
                if item[0].split('/')[-1] in allowed_concepts
            ]

            # Ajouter les noeuds filtrés
            for item in concept_sliced:
                concept_id = item[0].split('/')[-1]
                concept_name = item[1]
                concept_link = item[0]
                if concept_id in allowed_concepts and concept_id not in G:
                    G.add_node(concept_id, Concept_name=concept_name, Concept_link=concept_link)
                    print(f"🧠 Concept ajouté : ID={concept_id}, Nom={concept_name}, Niveau={levels}")

            # Ajouter les arêtes filtrées
            for i in range(len(concept_ids_filtered)):
                for j in range(i + 1, len(concept_ids_filtered)):
                    concept1 = concept_ids_filtered[i]
                    concept2 = concept_ids_filtered[j]
                    if not G.has_edge(concept1, concept2):
                        G.add_edge(concept1, concept2)

        # Générer les non-arêtes
        non_edges_list = list(nx.non_edges(G))
        print(f"🔍 {season}: {len(non_edges_list)} couples non connectés")

        # Calculer les scores Adamic-Adar
        adamic_preds = list(adamic_adar_index(G, tqdm(non_edges_list)))


        output_path = os.path.join(output_dir, f"{season}_adamic_scores.csv")
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Concept1", "Concept2", "AdamicAdarScore"])
            for u, v, score in adamic_preds:
                writer.writerow([u, v, score])
        print(f"✅ Fichier sauvegardé : {output_path}")    

# Example of use 
# generate_adamic_adar_scores_levels(["4","5"])


def generate_adamic_adar_scores_all_levels():

    # Creation du quaterly Dict 

    df = pd.read_csv("quantum_networks_subtree_papers_dates.csv")
    df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce')
    df = df.dropna(subset=['publication_date'])

    df['season_label'] = df['publication_date'].apply(get_season_label)

    season_order = {'winter': 1, 'spring': 2, 'summer': 3, 'fall': 4}
    df['season'] = df['season_label'].str.extract(r'(\w+)_\d+')[0]
    df['year'] = df['season_label'].str.extract(r'_(\d+)')[0].astype(int)
    df['season_rank'] = df['season'].map(season_order)

    grouped = df.groupby(['year', 'season_rank', 'season_label'])['paper_id'].apply(list)
    grouped = grouped.sort_index()

    cumulative_articles = set()
    season_articles_cumulative = {}

    for (_, _, label), paper_ids in grouped.items():
        cumulative_articles.update(paper_ids)
        season_articles_cumulative[label] = sorted(cumulative_articles) 

    '''for season, ids in season_articles_cumulative.items():
        print(f"{season}: {ids}")'''


    with open("quantum_networks_log_papers.csv", newline='', encoding='utf-8') as fichier_csv:
        lecteur = csv.DictReader(fichier_csv)
        article_data = {ligne['paper_id']: ligne for ligne in lecteur}


    for season, list_article in list(season_articles_cumulative.items()):  # un graphe par saison

        G = nx.Graph()

        concepts_list = []

        for article_id in list_article:

            article = article_data.get(article_id)

            print(article_id)

            concept_all = article.get("concepts").split(";")

            concept_sliced = [i.split("|") for i in concept_all] # gets all the individual concepts 

            for item in concept_sliced:

                concept_link = item[0]  
                concept_name = item[1]  
                concept_id = item[0].split('/')[-1]

                if concept_id not in G:

                    G.add_node(concept_id, Concept_name=concept_name, Concept_link=concept_link) # add the concept in the graph (node)

            for i in range(len(concept_sliced)): # here we connect all the concept together based on their appearance in each article
                for j in range(i + 1, len(concept_sliced)): 
                    concept1 = concept_sliced[i][0].split('/')[-1]
                    concept2 = concept_sliced[j][0].split('/')[-1]
                    if not G.has_edge(concept1, concept2): 
                        G.add_edge(concept1, concept2)

        # print(G.edges)

        non_edges_list = list(nx.non_edges(G)) # non-connected nodes

        print("Aperçu des couples de nœuds non connectés :")
        for u, v in non_edges_list[:10]:
            print(f"{u} - {v}")

        adamic_preds = list(adamic_adar_index(G, tqdm(non_edges_list))) # calculates adamic adar index for each pair of non-connected nodes

        filename = f"{season}_adamic_scores.csv"

        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Concept1", "Concept2", "AdamicAdarScore"])  # en-têtes

            for u, v, score in adamic_preds:

                writer.writerow([u, v, score])


# Function we call to put the name of the concepts in the graph

def get_display_name(concept_id):

    url = f'https://api.openalex.org/concepts/{concept_id}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get('display_name', concept_id)
        else:
            return concept_id
    except:
        return concept_id

    
def visualiser_top_adamic_from_file(fichier_csv, top_n):

    adamic_preds = []

    with open(fichier_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            concept1 = row["Concept1"]
            concept2 = row["Concept2"]
            score = float(row["AdamicAdarScore"])
            adamic_preds.append((concept1, concept2, score))

    top_edges = sorted(adamic_preds, key=lambda x: x[2], reverse=True)[:top_n]

    # Récupération des noms lisibles (display_name)
    all_concepts = set([u for u, _, _ in top_edges] + [v for _, v, _ in top_edges])
    concept_names = {cid: get_display_name(cid) for cid in tqdm(all_concepts, desc="Fetching concept names")}

    G = nx.Graph()
    for u, v, score in top_edges:
        G.add_edge(concept_names[u], concept_names[v], weight=score)

    pos = nx.spring_layout(G, seed=42, k=0.9)
    plt.figure(figsize=(10, 8))

    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=1000)
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.7)
    nx.draw_networkx_labels(G, pos, font_size=10)

    edge_labels = {}
    for u, v, data in G.edges(data=True):
        if 'weight' in data:
            poids = data['weight']
            label = f"{poids:.2f}"
            edge_labels[(u, v)] = label

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='gray', font_size=9)

    plt.title(f"Top {top_n} liens Adamic Adar depuis {fichier_csv}")
    plt.axis('off')
    plt.show()


# We start from some pairs of concepts using the ones with the highest score 

def get_top_adamic_scores(csv_file, top_n):

    scores = []

    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            concept1 = row["Concept1"]
            concept2 = row["Concept2"]
            score = float(row["AdamicAdarScore"])
            scores.append((concept1, concept2, score))

    top_scores = sorted(scores, key=lambda x: x[2], reverse=True)[:top_n]

    return top_scores


# Get the temporal evolution of the AA score over the seasons and years

def temporal_analysis():

    missing_data = [] # files (seasons) missing in the articles subset 

    season_order = ['winter', 'spring', 'summer', 'fall']

    previous_concepts = set() 

    # DYNAMIC : TRACKED PAIR TOP 10 ADAMIC SCORES 

    tracked_pairs = set()
    pair_scores = {}
    first_season_track = 0
    seasons_graph_x = []

    # Define the years scope (first available : 1984)

    for year in range(2010, 2024):  # 2024 not included

        for season in season_order:

            missing_tracked_concepts = []

            subfolder = f"adamic_scores_all_level"
            filename = os.path.join(subfolder, f"{season}_{year}_adamic_scores.csv")

            if os.path.exists(filename):

                first_season_track += 1

                if first_season_track == 1: # we take the concepts to track in the first available file 

                    track_amount = 20

                    top_concepts_scores = get_top_adamic_scores(filename, track_amount)

                    tracked_pairs = {
                        tuple(sorted((concept1, concept2)))
                        for concept1, concept2, _ in top_concepts_scores
                    }

                    pair_scores = {pair: [] for pair in tracked_pairs}

                seasons_graph_x.append(f"{season}_{year}")

                current_scores = {}

                current_concepts = set()

                print(f"Traitement fichier {filename}")

                with open(filename, newline='', encoding='utf-8') as csvfile:

                    reader = csv.DictReader(csvfile)
                    
                    # get ALL concepts
                    
                    for i, row in enumerate(reader):

                        concept1 = row["Concept1"]
                        concept2 = row["Concept2"]
                        score = float(row["AdamicAdarScore"])

                        pair = tuple(sorted((concept1, concept2))) # pour tous 

                        current_scores[pair] = score # dict with the pair of concept and their Adamic score 

                        current_concepts.add(pair) # concepts of the current season 

                # get SUBSET concepts

                for pair in tracked_pairs:

                    if pair in current_scores:

                        pair_scores[pair].append(current_scores[pair]) # add the score of the current season to the list of scores of the tracked pair

                    else:

                        pair_scores[pair].append(float("nan")) # the pair of concepts disapeared

                        missing_tracked_concepts.append(pair)

                # Comparaison 

                if previous_concepts:

                    common = current_concepts & previous_concepts
                    added = current_concepts - previous_concepts
                    removed = previous_concepts - current_concepts # pairs of concepts that diseappeared from the previous season to the current one

                    print(f"Comparaison avec la saison précédente :")
                    print(f"   ➕ Nouveaux liens : {len(added)}")
                    print(f"   ➖ Liens disparus : {len(removed)}")
                    print(f"   ✅ Liens communs  : {len(common)}")

                previous_concepts = current_concepts

            else:

                missing_data.append(filename)


            print(f"Missing pairs in {season} : {missing_tracked_concepts}")

# Print the missing seasons
# print(missing_data)

# Visualisation des données 

    concept_names = {}
    for pair in pair_scores:
        for concept_id in pair:
            if concept_id not in concept_names:
                concept_names[concept_id] = get_display_name(concept_id)

    plt.figure(figsize=(12, 6))

    for pair, scores in pair_scores.items():
        concept1_name = concept_names.get(pair[0], pair[0])
        concept2_name = concept_names.get(pair[1], pair[1])
        label = f"{concept1_name} - {concept2_name}"

        scores = np.array(scores, dtype=np.float32)  # s’assure que NaNs sont bien gérés
        plt.plot(seasons_graph_x, scores, marker='o', label=label)

    plt.xticks(rotation=45)
    plt.xlabel("Saison")
    plt.ylabel("Adamic-Adar Score")
    plt.title(f"Évolution du score Adamic-Adar pour 20 paires de concepts")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()