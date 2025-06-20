import os
import glob
from collections import defaultdict

import pandas as pd
import re
import requests
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

def parse_season(season, year):
    season_order_map = {'winter': 1, 'spring': 2, 'summer': 3, 'fall': 4}
    return (year, season_order_map.get(season.lower(), 0))

# 1. Collect filenames and parse season-year info
csv_dir = 'season_csvs'
pattern = re.compile(r'(spring|summer|fall|winter)_(\d{4})_jac_scores\.csv', re.IGNORECASE)

season_years = []

for filename in glob.glob(os.path.join(csv_dir, '*_jac_scores.csv')):
    basename = os.path.basename(filename)
    match = pattern.match(basename)
    if match:
        season, year = match.groups()
        season = season.lower()
        year = int(year)
        season_years.append((season, year))
    else:
        print(f"Filename pattern not matched: {basename}")

# 2. Generate full season list from 2000 onward
if season_years:
    parsed_seasons = [ (s, y) for s, y in season_years ]
    min_year = min(y for _, y in parsed_seasons if y >= 2000)
    max_year = max(y for _, y in parsed_seasons)

    season_order_map = {'winter': 1, 'spring': 2, 'summer': 3, 'fall': 4}
    # Generate all seasons from 2000 to max_year
    full_seasons = []
    for year in range(max(2000, min_year), max_year + 1):
        for season in ['winter', 'spring', 'summer', 'fall']:
            if year == min_year and parse_season(season, year)[1] < season_order_map[season]:
                # Skip seasons before min_year in that year
                continue
            full_seasons.append(f"{season}_{year}")

# 3. Read data
pair_time_series = defaultdict(dict)
for filename in glob.glob(os.path.join(csv_dir, '*_jac_scores.csv')):
    basename = os.path.basename(filename)
    match = pattern.match(basename)
    if match:
        season, year = match.groups()
        season = season.lower()
        year = int(year)
        # Skip years before 2000
        if year < 2000:
            continue
        df = pd.read_csv(filename)
        for _, row in df.iterrows():
            c1, c2, score = row['Concept1'], row['Concept2'], row['JaccardScore']
            pair = tuple(sorted([c1, c2]))
            season_name = f"{season}_{year}"
            pair_time_series[pair][season_name] = score

# 4. Build DataFrame with all pairs and seasons
# 4. Build DataFrame with all pairs and seasons
rows = []
for pair, season_scores in pair_time_series.items():
    row = {
        'Concept1': pair[0],
        'Concept2': pair[1],
        'Concepts': f"{pair[0]} & {pair[1]}"
    }
    for season in full_seasons:
        row[season] = season_scores.get(season, None)
    rows.append(row)

df_time = pd.DataFrame(rows)


# 5. Get top 10 pairs by average Jaccard score
df_time['AverageScore'] = df_time[full_seasons].mean(axis=1)
top_df = df_time.sort_values('AverageScore', ascending=False).head(10)

# 6. Fetch display names only for top 10 pairs
top_concepts = set(top_df['Concept1']) | set(top_df['Concept2'])
concept_names = {cid: get_display_name(cid) for cid in top_concepts}

# 7. Plot top 10 pairs
plt.figure(figsize=(20, 12))
for _, row in top_df.iterrows():
    concept1_name = concept_names.get(row['Concept1'], row['Concept1'])
    concept2_name = concept_names.get(row['Concept2'], row['Concept2'])
    label = f"{concept1_name} - {concept2_name}"

    scores = row[full_seasons]
    if scores.notnull().any():
        plt.plot(full_seasons, scores, marker='o', label=label)

plt.xlabel('Season')
plt.ylabel('Jaccard Index')
plt.title('Top 10 Concept Pair Evolution (from 2000 onwards)')
plt.xticks(rotation=45)
plt.legend(fontsize='small', bbox_to_anchor=(1,1))
plt.tight_layout()
plt.show()
