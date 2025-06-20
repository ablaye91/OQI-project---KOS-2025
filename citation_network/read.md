# Quantum Networks Citation Graphs

This project explores citation patterns within a selected subset of literature on **quantum networks**, using a knowledge graph approach. The goal was to create a knowledge graph per year of papers as nodes and the citations being the edges. 

Firstly, this was useful since the OpenAlex API request "counts_by_year", which gives the detailed citation number per year of a paper, is limited as it only goes back to maximum 2013. This would allow us to retrace the citations per year much further. 

Secondly, the citations are a sign of pertinence and popularity, which could be helpful to create a weighted graph with the most quoted papers being more revelant than the others. 

Thirdly, the citations in the pool of paper could help us create pairs of concept, with one concept being in paper A and the second concept in paper B, where paper A cites paper B. In turn, this could allow us to see the evolution of the relations between links through citations. This was tried in quantum_networks_analysis2.py using the jacquard index or just co-occurrences, the "test" result created top_pairs_over_time.png which was the cumulative score over time of pairs of concepts. Though I honestly don't remember if it was the score of the jacquard index or just co-occurrences.

## Data Collection

- Papers related to the *quantum networks* focal concept were retrieved and stored in quantum_networks_subtree_papers_dates.csv

## Node Selection

- A subset of **20-50 papers** was selected based on title, publication date, and identifier.
- These were stored in nodes.csv

## Citation Graph Construction

- Using the selected papers, a Turtle file was generated, named knowledge_graph.ttl
- This file includes up to **250 citations** per paper and adds the URLs of cited works.

## Citation Filtering

- To isolate intra-pool citations (i.e., citations **within the 20-50 selected papers**), the graph was filtered into filtered_citations.ttl

## Visualization

- Citation relationships were visualized using nodes (papers) and directed edges (citations).
- Temporal evolution was illustrated by creating graphs for different time intervals.
- First visualization: Only the oldest paper (1985).
- Second: Papers from 1985–1995.
- Additional visualizations follow this pattern to show the progression of citations over time.

## Notes
- An attempt was made to generate yearly citation counts using `counts_by_year`, but the result was too large to interpret effectively. With smaller pools, however, the results were manageable.

- By preserving **full publication dates**, the visualizations could later be adapted to show **quarterly** or **monthly** citation dynamics.

- The file visualisation has the graphs for 20 papers, visualisation2 has the graphs for 50 papers.