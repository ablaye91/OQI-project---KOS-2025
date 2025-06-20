import pandas as pd
import rdflib
import requests
from rdflib import Namespace
import matplotlib.pyplot as plt

def get_display_name(concept_id):
    url = f'https://api.openalex.org/concepts/{concept_id}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get('display_name', concept_id)
        else:
            print(f"Failed to fetch {concept_id}: {response.status_code}")
            return concept_id
    except Exception as e:
        print(f"Error fetching {concept_id}: {e}")
        return concept_id


# Files
TTL_FILE = 'filtered_citations.ttl'
CSV_FILE = 'quantum_networks_subtree_papers_dates100.csv'


# Load your CSV with papers and concepts
df = pd.read_csv('quantum_networks_subtree_papers_dates100.csv')

# Build a dictionary: paper_id -> set of concept IDs
paper_concept_pools = {}
for _, row in df.iterrows():
    paper_id = row['paper_id']
    concepts_str = row['concepts']
    concept_ids = set()
    if pd.notnull(concepts_str):
        for item in concepts_str.split(';'):
            if item:
                parts = item.split('|')
                if len(parts) >= 1:
                    cid = parts[0]
                    concept_ids.add(cid)
    paper_concept_pools[paper_id] = concept_ids

# Load graph
g = rdflib.Graph()
g.parse(TTL_FILE, format='turtle')
NS = Namespace("http://example.org/citation#")

# Load paper info
df = pd.read_csv(CSV_FILE)

# Map paper_id to publication date
pub_date_map = {}
for _, row in df.iterrows():
    pub_date = row['publication_date']
    if pd.notnull(pub_date):
        # Extract year
        year = pub_date.split('-')[0]
        pub_date_map[row['paper_id']] = int(year)
    else:
        pub_date_map[row['paper_id']] = None

# Build citation links
paper_citations = {}
for s, p, o in g.triples((None, NS.cites, None)):
    citing_id = str(s).split('#')[-1]
    cited_id = str(o).split('#')[-1]
    if citing_id not in paper_citations:
        paper_citations[citing_id] = set()
    paper_citations[citing_id].add(cited_id)

# Now, for each period (year), count concept pairs
# Initialize data structure: {(pair, year): count}
pair_year_counts = {}

for citing_paper, cited_papers in paper_citations.items():
    citing_year = pub_date_map.get(citing_paper)
    if citing_year is None:
        continue
    # Get concepts for citing paper
    if citing_paper not in paper_concept_pools:
        continue
    source_concepts = paper_concept_pools[citing_paper]
    for cited_paper in cited_papers:
        cited_year = pub_date_map.get(cited_paper)
        if cited_year is None:
            continue
        if cited_paper not in paper_concept_pools:
            continue
        target_concepts = paper_concept_pools[cited_paper]
        for sc in source_concepts:
            for tc in target_concepts:
                pair = tuple(sorted([sc, tc]))
                key = (pair, cited_year)
                pair_year_counts[key] = pair_year_counts.get(key, 0) + 1

# Convert to DataFrame
records = []
for (pair, year), count in pair_year_counts.items():
    records.append({
        'Concept1': pair[0],
        'Concept2': pair[1],
        'Year': year,
        'Score': count
    })

df_time = pd.DataFrame(records)
df_time.to_csv('concept_pairs_over_time.csv', index=False)

print(f"Saved concept pairs over time to 'concept_pairs_over_time.csv'.")

# --- Visualization: Plot top pairs over time ---
# For example, pick top N pairs by total recurrence
# Get top pairs by total recurrence
top_pairs = (
    df_time.groupby(['Concept1', 'Concept2'])['Score']
    .sum()
    .sort_values(ascending=False)
    .head(30)
)
top_pairs_list = top_pairs.index.tolist()

# Create a cache for concept display names
concept_names = {}

# Fetch display names only once per concept
unique_concepts = set([cid for pair in top_pairs_list for cid in pair])
for cid in unique_concepts:
    concept_names[cid] = get_display_name(cid)

# Plotting
plt.figure(figsize=(32, 20))
for pair in top_pairs_list:
    pair_df = df_time[(df_time['Concept1'] == pair[0]) & (df_time['Concept2'] == pair[1])]
    pair_df_sorted = pair_df.sort_values('Year')

    concept1_name = concept_names.get(pair[0], pair[0])
    concept2_name = concept_names.get(pair[1], pair[1])

    label = f"{concept1_name} - {concept2_name}"
    plt.plot(pair_df_sorted['Year'], pair_df_sorted['Score'], marker='o', label=label)

plt.xlabel('Year')
plt.ylabel('Recurrence Score')
plt.title('Top Concept Pairs Recurrence Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('top_pairs_over_time.png')
plt.show()
