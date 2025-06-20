from pathlib import Path
import os, itertools, collections
import requests
from tqdm import tqdm
from sklearn.preprocessing import MultiLabelBinarizer
import pandas as pd
import random

# Directory for storing results
root = r"C:/results/"
os.makedirs(root, exist_ok=True)

def fetch_counts_by_year(openalex_id):
    """
    Fetch yearly citation counts for a given OpenAlex work (paper) ID using the OpenAlex API.
    Returns a list of dictionaries with year and citation count.
    """
    url = f"https://api.openalex.org/works/{openalex_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        counts = data.get('counts_by_year', [])
        print(counts)
        return counts
    except Exception as e:
        print(f"Error fetching counts for {openalex_id}: {e}")
        return []

def mainlog():
    """
    For each paper in the input CSV, fetches yearly citation counts from OpenAlex
    and adds them as columns ('cited_by_{year}') to the output CSV.
    """
    input_csv = "quantum_networks_papers.csv"
    output_csv = "quantum_networks_papers_cites.csv"

    df = pd.read_csv(input_csv)

    years_range = list(range(2013, 2025))
    # Initialize columns for each year, default 0
    for y in years_range:
        df[f'cited_by_{y}'] = 0

    for index, row in tqdm(df.iterrows(), total=len(df)):
        print("Nombre de lignes dans le CSV :", len(df))
        paper_id = row['paper_id']
        openalex_id = paper_id.split('/')[-1]
        counts = fetch_counts_by_year(openalex_id)

        # Make a quick-access dict: year -> count object
        counts_dict = {item['year']: item for item in counts}

        for y in years_range:
            count_obj = counts_dict.get(y)
            # Set the citation count for this year
            if count_obj:
                df.at[index, f'cited_by_{y}'] = count_obj.get('cited_by_count', 0)
            else:
                df.at[index, f'cited_by_{y}'] = 0

    # Save the augmented dataframe
    df.to_csv(output_csv, index=False)
    print(f"Augmented CSV saved as {output_csv}")

def analysis11_with_citations(level_threshold: int = 4):
    """
    Main analysis function. Builds yearly concept–co-occurrence edge lists for papers,
    keeping only concepts with OpenAlex level >= `level_threshold`.
    Adds citation columns to each edge file:
        - citation_sum_year: citations in year Y
        - citation_sum_year2: citations in years Y and Y+1
    """

    ROOT = r"C:/results/"
    EDGE_DIR = Path(ROOT, "raw_graph1")
    EDGE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load input tables
    data = pd.read_csv("quantum_networks_papers_cites.csv")
    levels = pd.read_csv("concepts_levels.csv")  # columns: concept_id, level

    # Keep only concept_ids with level ≥ threshold
    allowed_ids = set(levels.loc[levels["level"] >= level_threshold, "concept_id"])

    # Restrict to years of interest
    data = data[(data.publication_year >= 2013) & (data.publication_year < 2025)]
    data = data.drop(columns=['title', 'journal', 'authors'])  # Drop unused columns

    # 2. Parse the 'concepts' column into a list of (id, name, score) tuples
    def parse_concepts(concept_str):
        """
        Parses the 'concepts' string from the input CSV into a list of tuples.
        Each tuple: (concept_id, concept_name, score)
        """
        concepts = []
        for part in concept_str.split(';'):
            items = part.split('|')
            if len(items) == 3:
                c_id, c_name, c_score = items
                concepts.append((c_id, c_name, float(c_score)))
            else:
                raise ValueError(f"Unexpected format in concept string: {part}")
        return concepts

    data["parsed_concepts"] = data["concepts"].apply(parse_concepts)
    df = data.drop(columns="concepts")

    # Convert from wide to long format: one row per (paper, concept)
    long_df = df.explode("parsed_concepts").reset_index(drop=True)
    long_df[["concept_id", "concept", "score"]] = pd.DataFrame(
        long_df["parsed_concepts"].tolist(), index=long_df.index
    )

    # Keep only paper-concept relations with score > 0 and allowed concept ids
    long_df = (
        long_df[["paper_id", "publication_year", "concept_id", "concept", "score"]]
        .query("score > 0.0")
        .drop_duplicates()
        .reset_index(drop=True)
    )
    long_df = long_df[long_df["concept_id"].isin(allowed_ids)].reset_index(drop=True)

    # Save the filtered table
    long_df.to_csv(Path(ROOT, "concepts_long1.csv"), index=False)
    print(f"✔ kept {len(long_df):,} paper–concept relations after level ≥ {level_threshold}")

    # 3. Prepare “bag of concepts” per paper for each year
    df = long_df[["paper_id", "publication_year", "concept"]].drop_duplicates()
    # Clean up concept names
    df["concept"] = (
        df["concept"]
        .str.strip()
        .str.lower()
        .str.replace(r'\s+', '_', regex=True)
    )

    # Group into concept lists (bags) per paper per year
    paper_bags = (
        df.groupby(["publication_year", "paper_id"])["concept"]
        .apply(lambda s: sorted(set(s)))
        .reset_index(name="concept_list")
    )

    # 4. Build a lookup table for citations: (paper_id, year) -> number of citations
    citation_lookup = {}
    for col in data.columns:
        if col.startswith("cited_by_"):
            year = int(col.replace("cited_by_", ""))
            for i, row in data.iterrows():
                citation_lookup[(row["paper_id"], year)] = row[col]

    # 5. Build yearly concept co-occurrence edge lists
    def yearly_edge_list(bags_year, year):
        """
        Builds the undirected co-occurrence edge list for a year.
        Each edge is (source concept, target concept, weight), where weight is number of co-occurrences.
        Also adds citation sums for the given year and year+1.
        """
        mlb = MultiLabelBinarizer(sparse_output=True)
        M = mlb.fit_transform(bags_year["concept_list"])
        concepts = mlb.classes_

        # Compute co-occurrence matrix
        C = (M.T @ M)
        C.setdiag(0)
        C.eliminate_zeros()

        coo = C.tocoo()
        edges = pd.DataFrame({
            "source": concepts[coo.row],
            "target": concepts[coo.col],
            "weight": coo.data
        })

        # For each concept pair, sum citations of papers where they co-occur
        paper_year = bags_year.set_index("paper_id")
        paper_ids = paper_year.index.unique()

        pair2cites1 = collections.defaultdict(float)  # Citations in year Y
        pair2cites2 = collections.defaultdict(float)  # Citations in years Y and Y+1

        for pid in paper_ids:
            concept_list = paper_year.loc[pid]["concept_list"]
            if isinstance(concept_list, list):
                concepts = sorted(set(concept_list))
            else:
                # If it's a Series of one list
                concepts = sorted(set(concept_list.iloc[0]))

            c1c2_pairs = itertools.combinations(concepts, 2)

            cites_y1 = citation_lookup.get((pid, year), 0)
            cites_y2 = cites_y1 + citation_lookup.get((pid, year + 1), 0)

            for c1, c2 in c1c2_pairs:
                key = tuple(sorted((c1, c2)))
                pair2cites1[key] += cites_y1
                pair2cites2[key] += cites_y2

        # Add citation sums to edge DataFrame
        edges["citation_sum_year"] = [
            pair2cites1.get(tuple(sorted((s, t))), 0.0)
            for s, t in zip(edges["source"], edges["target"])
        ]
        edges["citation_sum_year2"] = [
            pair2cites2.get(tuple(sorted((s, t))), 0.0)
            for s, t in zip(edges["source"], edges["target"])
        ]

        return edges

    # For each year, build the edge list and save as CSV
    for year, bags_year in tqdm(paper_bags.groupby("publication_year"),
                                total=paper_bags["publication_year"].nunique(),
                                desc="Building enriched yearly edges"):
        edges = yearly_edge_list(bags_year, year)

        if not edges.empty:
            # Keep only top 5% most frequent edges
            qcut = edges["weight"].quantile(0.95)
            edges = edges[edges["weight"] >= qcut]

        edges.to_csv(EDGE_DIR / f"edges_{year}.csv", index=False)
        print(f"✅ {year}: {len(edges):,} edges saved with citations")

#mainlog()  # Uncomment to run the data augmentation step first
analysis11_with_citations()  # Builds co-occurrence graphs