# OQI-project---KOS-2025





## Automatic Knowledge Graph Generation with NLP and Ontology Alignment

This part of the project aims to generate a **Knowledge Graph (KG)** from a collection of quantum computing research paper abstracts. Using Natural Language Processing (NLP) and ontology alignment, we extract structured information in the form of (subject, predicate, object) triples and attempt to align them with a formal **Physics Ontology**. This explores the instanciation of the following research article : "**Generating knowledge graphs by employing NaturalLanguage Processing and Machine Learning techniques within the scholarly domain** " by Dessi and al (availaible in the directory /KG_generation_NLP).

---

### Work Accomplished

- **Entity Extraction**: Named Entity Recognition using SpaCy (`en_core_web_sm`) was successful in annotating abstracts with key entities.
- **Triple Extraction**: Dependency-based extraction of SVO (Subject-Verb-Object) triples worked as expected.
- **Ontology Loading**: The Physics ontology was successfully parsed using `rdflib` in RDF, OWL, and TTL formats.
- **Triple Mapping (Partially)**: Some triples were mapped to ontology terms using exact or partial string matching.

---

### Ontology Description

The physics ontology (`PhySci.ttl`, `physci.rdf`) is a semantic knowledge model of physical science concepts, including:

- **Classes**: `Quantum_Entanglement`, `Black_Hole`, `Quantum_State`, etc.
- **Properties**: `hasName`, `hasDescription`, `partOf`, etc.
- **Instances**: Named examples or cases of phenomena.

We use it to validate or enhance extracted triples. For example, if a triple `(entanglement, affect, state)` is extracted and the ontology has `entanglement` and `state` as classes, this triple gains semantic grounding.

---

### 📁 File Structure

| File / Folder                            | Description                                                        |
| ---------------------------------------- | ------------------------------------------------------------------ |
| `quantum_computing_subtree_papers.csv`   | Source dataset containing abstracts and metadata of papers         |
| `PhySci.ttl`, `physci.rdf`, `physci.owl` | Physics ontology provided in various serialization formats         |
| `[OQI]_Automatic_KG_gen_NLP.ipynb`       | Main notebook for entity/triple extraction and ontology mapping    |
| `Dessì et al. - 2021 - ... .pdf`         | Reference paper for the triple extraction and KG generation method |


---

### ⚙️ How to Run

#### Setup Environment
```bash
pip install pandas spacy rdflib
python -m spacy download en_core_web_sm
``` 
Run the notebook
Open and run [OQI]_Automatic_KG_gen_NLP.ipynb step-by-step.

It will :
-   Loads abstracts
-   Extracts triples
-   Loads the ontology
-   Maps extracted triples to ontology concepts
-   Saves results to CSV
-   Review enhanced_triples.csv. This file contains both raw and ontology-aligned triples.

### Limitations & Future Work
Due to time constraints, several key features of this project remain either partially implemented or left as future improvements. These include:

#### Concept-Based Triple Filtering
We initially attempted to filter and validate extracted triples against the concept lists provided in the paper metadata. However, this approach was unreliable due to:

Surface form mismatches (e.g., "quantum entanglement" vs. "entangled states"),

Synonyms and lexical variations not accounted for.
Future work could include string normalization or embedding-based matching to improve alignment.

#### Date Literal Conversion
Parsing of ontology data using RDFLib triggered repeated errors for non-ISO date formats like '01-07-2019'.
Although some formats were manually fixed or bypassed during parsing, the warnings persist and may affect downstream ontology operations.
Future work: implement a preprocessing step to normalize all date literals before ontology loading.

####  Triple–Ontology Mapping
Triple-to-ontology mapping was only partially realized:

Many triples extracted via NLP did not match ontology terms exactly.

The lack of semantic understanding in string comparison (e.g., "uses" vs. "applies") limited recall.
Future work could leverage:
-   Named entity linking (NEL),
-   Sentence embedding models (e.g., BERT, SBERT),
-   Ontology alignment libraries like LOV, ELK, or OntoPortal.