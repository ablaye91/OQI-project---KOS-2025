# Documentation

This file has several modules explained below. To use them, please pull the entire file to avoid missing files and wrong directories.

## Overview

1. **import.py**
   Fetches metadata for papers related to the focal concept "Quantum Networks" from the OpenAlex API and exports them for further analysis.
2. **analysis.py**
   Processes the paper metadata, retrieves yearly citation counts, extracts concept information, and builds yearly concept co-occurrence graphs enriched with citation data.
3. **graph.py**
   Explores the statistical relationships between the number of papers co-mentioning concept pairs and their citation metrics, generating key figures and regression analyses to reveal scaling laws and productivity patterns.
4. **success.py**
   Computes global metrics for each concept pair (such as total papers, citations, and growth rates), ranks pairs in various ways (e.g., by impact or growth), and produces visualizations of their yearly and cumulative evolution.
5. **individual_adamic_adar.py**
   Tracks and visualizes the Adamic-Adar index (a network proximity measure) for a selected pair of concepts over time, helping to identify periods of increased relatedness or collaboration between topics.

Together, these scripts provide a full pipeline from raw data acquisition to advanced scientometric analysis and visualization of the evolving structure of the quantum networks research field.

## Import

Fetches metadata for papers related to the focal concept "Quantum Networks" from the OpenAlex API and exports them as a CSV file for further analysis.

### Output

- `quantum_networks_papers.csv`: A CSV file with one row per paper and the following columns:
    - `paper_id`
    - `title`
    - `publication_year`
    - `journal`
    - `authors`
    - `citation_count`
    - `concepts` (concatenated string: `concept_id|concept_name|score;...`)

### Notes

- The API is rate-limited. The script waits 0.2 seconds between requests to avoid hitting the limit.
- You can stop fetching early by uncommenting the break condition in the loop if you want fewer results.
- The script is easily adaptable for other OpenAlex concept IDs.


## Analysis

1. **Fetches yearly citation counts** for each paper using the OpenAlex API.
2. **Processes concepts** assigned to each paper, keeping only those above a certain semantic level.
3. **Builds yearly co-occurrence graphs** of concepts, where edges represent the number of papers in which two concepts co-occurred.
4. **Enriches graph edges with citation metrics**: sum of citations in the same year, and sum in the year and the next year.
5. **Saves edge lists as CSV files** for each year.

### Notes

- The file quantum_networks_papers.csv is a subset of around 26'000 papers from the focal concept "Quantum Networks".
- The OpenAlex API has rate limits and fetching citations may take a while, this subset took 3 hours, the full dataset is much bigger so beware.
- Adjust level_threshold to choose the minimum level of concept accepted, you need concepts_level.csv to do so.

### Files

- `quantum_networks_papers.csv`: List of papers with columns: `paper_id`, `publication_year`, `concepts`, ...
- `quantum_networks_papers_cites.csv`: List of papers with the same columns AND : `cited_by_2013`, `cited_by_2014`, ..., `cited_by_2024`
- `concepts_levels.csv`: Mapping of concept IDs to their OpenAlex levels (`concept_id`, `level`).

### 1. Fetch Citation Counts (`mainlog`)

For every paper in `quantum_networks_papers.csv`, query OpenAlex to get its yearly citation counts and append them as columns (`cited_by_{year}`) in a new file: `quantum_networks_papers_cites.csv`.

**Note:** This step hits the OpenAlex API and may take time.
**Run:** Uncomment and run `mainlog()` in the code.

### 2. Build and Enrich Co-occurrence Graphs (`analysis11_with_citations`)

- Loads `quantum_networks_papers_cites.csv` and filters papers to a target year range.
- Parses the `concepts` column, producing one row per (paper, concept) relation.
- Keeps only concepts with OpenAlex level ≥ `level_threshold` (default: 4).
- For each year:
    - Forms a "bag of concepts" for each paper.
    - Builds a concept–concept co-occurrence matrix (edges weighted by number of co-occurrences).
    - For each edge (concept pair), sums the citations of all papers in which they co-occur for that year and for that year plus the following year.
    - Keeps only the top 5% most frequent edges (by co-occurrence count) for clarity.
    - Saves as `C:/results/raw_graph1/edges_{year}.csv`.

### Output

- `quantum_networks_papers_cites.csv`: Input data with yearly citation counts.
- `C:/results/concepts_long1.csv`: Long-format table of filtered paper–concept relations.
- `C:/results/raw_graph1/edges_{year}.csv`: Yearly concept co-occurrence edge lists with citation enrichments.

### Usage

1. (ONLY IF YOU WANT TO USE ANOTHER SUBSET!!)**Run the citation fetching step** (once, as it is slow), by uncommenting and calling `mainlog()`.
2. **Run the analysis step** with `analysis11_with_citations()`. You can change the `level_threshold` parameter as needed.

## Graph

Analyzes yearly concept pair co-occurrence graphs, focusing on the relationship between the number of papers (weight) and citation metrics. It produces several figures that help understand the statistical structure and dynamics of concept co-occurrence in a scientific field.

### Input

- Edge CSV files: Each file (`edges_YYYY.csv`) in `C:/results/raw_graph1/` should contain columns such as `source`, `target`, `weight`, and `citation_sum_year`.

### Outputs

- Figures (as PNG):
    - `weight_vs_citations.png`
    - `loglog_regression.png`
    - `citation_per_paper.png`
    - `mean_citations.png`
    - `distribution_of_citations.png`
    - `variance_yearly_citations.png`
- Printed log/log regression statistics and linear regression results (in console).

### Key Figures and Interpretation

#### **Figure 2: Scatter Plot (Weight vs. Citations) – loglog_regression.png**
Each point represents a concept pair for a given year. The red line is the linear regression fit on log-transformed data.

- **Slope of 1.10:** This means the relation between the number of papers and the number of citations follows a power law:
  `citations ≈ weight^1.10`
- **Superlinearity:** When the number of papers doubles, the number of citations increases by slightly more than double.

#### **Figure 3: Citations per Article vs. Number of Articles - citation_per_paper.png**
- **X-axis (log):** Number of articles for a pair (weight)
- **Y-axis (log):** Average number of citations per article for this pair and year (`citations_per_paper = citations / weight`)

However, as this figure shows, the curve is flat: each article brings about the same number of citations, regardless of the pair’s size. So, there is no critical mass effect, no "acceleration" of return as weight increases.

**Interpretation:**
The superlinear relationship seen in Figure 2 may just result from the fact that highly-studied pairs have more articles and thus more total citations—but not more citations per article. Despite the positive relation between total article and citation counts, this does not come from increased yield per article, but simple arithmetic accumulation: more articles means more citations, but each article is, on average, just as "productive" as others.

## Success

Analyzes pairs of scientific concepts from yearly co-occurrence edge lists, computes metrics, ranks pairs in various ways (total citations, growth, newcomers, etc.), and visualizes their evolution over time.

### Overview

- **Step 1:** Computes summary metrics for every concept pair (e.g. total weight, total citations, growth rates, etc.).
- **Step 2:** Selects the top pairs according to different ranking modes (total citations, recent growth, newcomers, etc.).
- **Step 3:** Visualizes the yearly and cumulative evolution (papers and citations) for each selected pair.
- **Step 4:** Optionally, lists all "newcomer" pairs (pairs appearing for the first time after a given year).

All visualizations are saved in `C:/results/figures2/selected_pairs2/`, with one folder per ranking mode.

### Input

- Yearly edge lists in `C:/results/raw_graph1/edges_YYYY.csv`
  Each file must include: `source`, `target`, `weight`, `citation_sum_year`.

### Output

- For each ranking mode (e.g. `cites_total`, `cites_growth`, ...), a folder with:
    - For each selected pair:
        - `[conceptA]__[conceptB].png` (yearly papers and citations)
        - `[conceptA]__[conceptB]_cumulative.png` (cumulative papers and citations)
- (Optional) A text file with all newcomer pairs: `all_newcomer_pairs.txt`

### Main Functions

- **build_edge_metrics:**
  Loads all yearly edge CSVs and computes, for each pair:
    - Total and recent paper/citation counts
    - First and last year of appearance
    - Growth rates over the last 3 years

- **select_pairs:**
  Ranks pairs according to a chosen metric, e.g. total citations, recent growth, etc.

- **visualise_pairs:**
  For selected pairs, plots:
    - Yearly number of papers and citations per year (dual y-axis)
    - Cumulative number of papers and cumulative citations

- **run_all_rankings:**
  Runs all ranking modes and generates figures for each.

- **list_all_newcomer_pairs:**
  Lists all pairs whose first appearance is after a given threshold year (default: 2017).

### Ranking Modes

- **cites_total:** Top pairs by total citations (all years)
- **cites_last:** Top pairs by most citations in the latest year
- **cites_growth:** Top pairs by citation growth rate (last 3 years vs. previous 3 years)
- **weight_total:** Top pairs by total number of papers (all years)
- **weight_growth:** Top pairs by paper growth rate (last 3 years vs. previous 3 years)
- **newcomer:** Pairs whose first appearance is in or after 2017, ranked by total citations

## Figure Explanation

Each selected pair gets two figures:

1. **Yearly Evolution:**
   - X-axis: Year
   - Left Y-axis (blue): Number of papers per year (weight)
   - Right Y-axis (orange): Number of citations in that year

2. **Cumulative Evolution:**
   - X-axis: Year
   - Left Y-axis (blue): Cumulative number of papers
   - Right Y-axis (red): Cumulative number of citations

### Customization

- Change the `k` parameter in `run_all_rankings` to select more or fewer pairs per mode.
- To export all newcomer pairs, use the commented code at the end of the script.

## Individual Adamic Adar index

This script visualizes the temporal evolution of the Adamic-Adar score for a specific pair of concepts, based on their OpenAlex concept IDs. The Adamic-Adar score is a network proximity metric often used in link prediction and scientometrics.
It's the one Carolina made, please go to her folder for more details.
