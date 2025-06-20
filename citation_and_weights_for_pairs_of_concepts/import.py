import time
import pandas as pd
import requests

def fetch_quantum_network_works():
    """
    Fetch works related to Quantum Networks, handling pagination to get more than 200 results.
    """
    url = "https://api.openalex.org/works"
    params = {
        "filter": "concepts.id:c186468114",
        "sort": "cited_by_count:desc",
        "per_page": 200,
        # You can also add cursor-based pagination if needed
    }
    all_results = []
    cursor = "*"

    while True:
        params["cursor"] = cursor
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        all_results.extend(results)

        meta = data.get("meta", {})
        cursor = meta.get("next_cursor")
        if not cursor:
            break

        # Optional: break after a certain number of papers
        # if len(all_results) >= 1000:
        #     break

        time.sleep(0.2)  # To respect rate limits

    return all_results

def export_works_to_csv(works, filename="quantum_networks_papers.csv"):
    """
    Export works with publication dates to CSV.
    """
    records = []
    for work in works:
        paper_id = work.get("id", "N/A").replace("https://openalex.org/", "")
        title = work.get("display_name", "N/A")
        pub_year = work.get("publication_year", "N/A")
        journal = work.get("host_venue", {}).get("display_name", "N/A")
        authors = ", ".join(
            auth.get("author", {}).get("display_name", "N/A") for auth in work.get("authorships", [])
        )
        citation_count = work.get("cited_by_count", "N/A")
        concepts_str = ";".join(
            f"{concept.get('id','N/A')}|{concept.get('display_name','N/A')}|{concept.get('score',1)}"
            for concept in work.get("concepts", [])
        )
        records.append({
            "paper_id": paper_id,
            "title": title,
            "publication_year": pub_year,
            "journal": journal,
            "authors": authors,
            "citation_count": citation_count,
            "concepts": concepts_str
        })

    df = pd.DataFrame(records)
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"Exported works to {filename}")

if __name__ == "__main__":
    works = fetch_quantum_network_works()
    export_works_to_csv(works)