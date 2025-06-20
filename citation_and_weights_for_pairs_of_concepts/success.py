from pathlib import Path
import os, re
from typing import List, Tuple
import matplotlib.pyplot as plt
import pandas as pd
import random

root = r"C:/results/"
os.makedirs(root, exist_ok=True)
EDGE_DIR = Path(os.path.join(root,"raw_graph1"))
os.makedirs(EDGE_DIR, exist_ok=True)

ROOT = r"C:/results/"
EDGE_DIR = Path(ROOT, "raw_graph1")
FIG_DIR = Path(ROOT, "figures2", "selected_pairs2")
FIG_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------------------------
# 1.  métriques pour chaque paire
# -------------------------------------------------------------------
def build_edge_metrics(edge_dir: Path) -> pd.DataFrame:
    rows, pat = [], re.compile(r"edges_(\d{4})\.csv")
    for f in edge_dir.glob("edges_*.csv"):
        year = int(pat.search(f.name).group(1))
        df = pd.read_csv(f)
        if df.empty:
            continue
        df["pair"] = df.apply(
            lambda r: tuple(sorted((r["source"], r["target"]))), axis=1)
        # --- Fix duplicates: divide by 2 ---
        df["weight"] = df["weight"] / 2
        df["citation_sum_year"] = df["citation_sum_year"] / 2
        # Optionally:
        # df["citation_sum_year2"] = df["citation_sum_year2"] / 2
        # -------------------------------
        df["year"] = year
        rows.append(df)

    big = pd.concat(rows, ignore_index=True)

    grouped = (big.groupby("pair")
                 .agg(weight_total=("weight", "sum"),
                      cites_total=("citation_sum_year", "sum"),
                      year_first=("year", "min"),
                      year_last=("year", "max"))
                 .reset_index())

    latest_year = big["year"].max()
    latest = big[big["year"] == latest_year] \
             .groupby("pair") \
             .agg(weight_last=("weight", "sum"),
                  cites_last=("citation_sum_year", "sum"))

    grouped = grouped.merge(latest, on="pair", how="left")

    Δ = 3
    def last_n(s, n):
        return s.sort_values().tail(n).sum()

    tmp = (big.groupby("pair")
             .agg(w_last3=("weight", lambda s: last_n(s, Δ)),
                  w_prev3=("weight",
                           lambda s: last_n(s.iloc[:-Δ] if len(s) > Δ else s*0, Δ)),
                  c_last3=("citation_sum_year", lambda s: last_n(s, Δ)),
                  c_prev3=("citation_sum_year",
                           lambda s: last_n(s.iloc[:-Δ] if len(s) > Δ else s*0, Δ)))
             .reset_index())

    grouped = grouped.merge(tmp, on="pair", how="left")
    grouped["weight_growth"] = (grouped["w_last3"]+1)/(grouped["w_prev3"]+1)
    grouped["cites_growth"]  = (grouped["c_last3"]+1)/(grouped["c_prev3"]+1)
    return grouped


# -------------------------------------------------------------------
# 2.  différents classements
# -------------------------------------------------------------------
def select_pairs(metrics: pd.DataFrame,
                 mode: str,
                 k: int = 5,
                 seed: int = 42) -> List[Tuple[str, str]]:

    random.seed(seed)
    m = metrics.copy()

    if mode == "cites_total":
        pairs = m.sort_values("cites_total", ascending=False).head(k)["pair"]
    elif mode == "cites_last":
        pairs = m.sort_values("cites_last", ascending=False).head(k)["pair"]
    elif mode == "cites_growth":
        pairs = (m.query("cites_total >= 10")
                   .sort_values("cites_growth", ascending=False)
                   .head(k)["pair"])
    elif mode == "weight_total":
        pairs = m.sort_values("weight_total", ascending=False).head(k)["pair"]
    elif mode == "weight_growth":
        pairs = (m.query("weight_total >= 10")
                   .sort_values("weight_growth", ascending=False)
                   .head(k)["pair"])
    elif mode == "newcomer":
        pairs = (m.query("year_first >= 2017")
                   .sort_values("cites_total", ascending=False)
                   .head(27)["pair"])
    else:
        raise ValueError("Unknown mode")

    return pairs.tolist()


# -------------------------------------------------------------------
# 3.  visualisation (axes communs)
# -------------------------------------------------------------------
def visualise_pairs(pairs: List[Tuple[str, str]],
                    edge_dir: Path,
                    out_dir: Path,
                    show: bool = False):

    out_dir.mkdir(parents=True, exist_ok=True)

    rows, pat = [], re.compile(r"edges_(\d{4})\.csv")
    for f in edge_dir.glob("edges_*.csv"):
        year = int(pat.search(f.name).group(1))
        df = pd.read_csv(f)
        if df.empty:
            continue
        df["pair"] = df.apply(
            lambda r: tuple(sorted((r["source"], r["target"]))), axis=1)
        # --- Fix duplicates: divide by 2 ---
        df["weight"] = df["weight"] / 2
        df["citation_sum_year"] = df["citation_sum_year"] / 2
        # Optionally:
        # df["citation_sum_year2"] = df["citation_sum_year2"] / 2
        # -------------------------------
        df["year"] = year
        rows.append(df)
    big = pd.concat(rows, ignore_index=True)
    all_years = range(big["year"].min(), big["year"].max()+1)

    # pré-calcul des limites
    max_w = max_c = max_w_c = max_c_c = 0
    prepared = {}
    for pair in pairs:
        dfp = (big[big["pair"] == pair]
               .groupby("year", as_index=False)
               .agg(weight=("weight", "sum"),
                    citation_sum_year=("citation_sum_year", "sum"))) \
            .set_index("year") \
            .reindex(all_years, fill_value=0) \
            .reset_index()

        dfp["weight_cum"] = dfp["weight"].cumsum()
        dfp["citation_sum_year"] = dfp["citation_sum_year"]  # per-year
        dfp["citation_sum_cum"] = dfp["citation_sum_year"].cumsum()  # cumulative
        prepared[pair] = dfp

        max_w   = max(max_w,   dfp["weight"].max())
        max_c   = max(max_c,   dfp["citation_sum_year"].max())
        max_w_c = max(max_w_c, dfp["weight_cum"].max())
        max_c_c = max(max_c_c, dfp["citation_sum_cum"].max())

    for pair in pairs:
        dfp = prepared[pair]
        #print(dfp)
        a, b = pair
        safe = re.sub(r"[^\w\-]+", "_", f"{a}__{b}")

        # --- normal -------------------------------------------------
        fig, ax1 = plt.subplots(figsize=(10,4))
        ax1.plot(dfp["year"], dfp["weight"], marker="o",
                 color="steelblue", label="weight")
        ax1.set_ylim(0, max_w*1.05)
        ax1.set_ylabel("Nbr papiers", color="steelblue")
        ax1.tick_params(axis='y', labelcolor="steelblue")

        ax2 = ax1.twinx()
        ax2.plot(dfp["year"], dfp["citation_sum_year"], marker="s",
                 linestyle="--", color="darkorange")
        ax2.set_ylim(0, dfp["citation_sum_year"].max() * 1.05)
        ax2.set_ylabel("Citations (année)", color="darkorange")
        ax2.tick_params(axis='y', labelcolor="darkorange")

        ax1.set_xlabel("Année")
        ax1.set_title(f"{a}  ↔  {b}")
        fig.tight_layout()
        fig.savefig(out_dir / f"{safe}.png", dpi=150)
        if show: plt.show()
        plt.close(fig)

        # --- cumul --------------------------------------------------
        fig, ax1 = plt.subplots(figsize=(10,4))
        ax1.plot(dfp["year"], dfp["weight_cum"], marker="o",
                 color="royalblue")
        ax1.set_ylim(0, max_w_c*1.05)
        ax1.set_ylabel("Papiers cum.", color="royalblue")
        ax1.tick_params(axis='y', labelcolor="royalblue")

        ax2 = ax1.twinx()
        ax2.plot(dfp["year"], dfp["citation_sum_cum"], marker="s",
                 linestyle="--", color="orangered")
        ax2.set_ylim(0, max_c_c*1.05)
        ax2.set_ylabel("Citations cum.", color="orangered")
        ax2.tick_params(axis='y', labelcolor="orangered")

        ax1.set_xlabel("Année")
        ax1.set_title(f"{a}  ↔  {b}  –  cumul")
        fig.tight_layout()
        fig.savefig(out_dir / f"{safe}_cumulative.png", dpi=150)
        if show: plt.show()
        plt.close(fig)


# -------------------------------------------------------------------
# 4.  exécuter tous les classements dans des dossiers séparés
# -------------------------------------------------------------------
def run_all_rankings(k: int = 5, seed: int = 42):
    metrics = build_edge_metrics(EDGE_DIR)
    modes = ["cites_total", "cites_last", "cites_growth",
             "weight_total", "weight_growth", "newcomer"]

    for mode in modes:
        pairs = select_pairs(metrics, mode, k=k, seed=seed)
        out_dir = FIG_DIR / mode
        visualise_pairs(pairs, EDGE_DIR, out_dir, show=False)
        print(f"➡️  {mode}: {len(pairs)} paires sauvegardées dans {out_dir}")

# lancez-le :
def list_all_newcomer_pairs(metrics: pd.DataFrame, threshold_year: int = 2017) -> List[Tuple[str, str]]:
    """
    Liste toutes les paires de concepts qui sont des 'newcomers', c'est-à-dire dont le premier lien date de threshold_year ou après.
    """
    newcomers = metrics[metrics["year_first"] >= threshold_year]
    return newcomers["pair"].tolist()

# Utilisation :
#metrics = build_edge_metrics(EDGE_DIR)
#newcomer_pairs = list_all_newcomer_pairs(metrics, threshold_year=2017)
#print(f"{len(newcomer_pairs)} paires newcomers trouvées (year_first >= 2017) :")
#for pair in newcomer_pairs:
    #print(pair)
#with open(ROOT + "all_newcomer_pairs.txt", "w", encoding="utf8") as f:
    #for a, b in newcomer_pairs:
        #f.write(f"{a}\t{b}\n")

run_all_rankings(k=10, seed=123)