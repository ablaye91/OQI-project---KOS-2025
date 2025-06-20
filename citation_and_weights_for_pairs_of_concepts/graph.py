from pathlib import Path
import os, itertools, collections
import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
from sklearn.linear_model import LinearRegression
import pandas as pd

# Directory for storing results
root = r"C:/results/"
os.makedirs(root, exist_ok=True)
EDGE_DIR = Path(root, "raw_graph1")
DIG_DIR = Path(root, "figures2")
FIG_DIR = Path(DIG_DIR, "graphs")
EDGE_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

# 1. LOAD DATA ----------------------------------------

rows = []
pat = re.compile(r"edges_(\d{4})\.csv")
for f in EDGE_DIR.glob("edges_*.csv"):
    year = int(pat.search(f.name).group(1))
    df = pd.read_csv(f)
    if df.empty:
        continue
    df["year"] = year
    df["pair"] = df.apply(lambda r: tuple(sorted((r["source"], r["target"]))), axis=1)
    rows.append(df[["pair", "year", "weight", "citation_sum_year"]])
big = pd.concat(rows, ignore_index=True)

print(f"Loaded {len(big):,} rows for {big['pair'].nunique():,} unique pairs.")

# 2. RELATIONSHIP: WEIGHT vs CITATIONS -----------------

plt.figure(figsize=(6, 5))
plt.scatter(big["weight"], big["citation_sum_year"], alpha=0.2)
plt.xscale("log")
plt.yscale("log")
plt.xlabel("Weight (number of papers, log)")
plt.ylabel("Citations (log)")
plt.title("Weight vs. Citations per pair per year")
plt.tight_layout()
plt.savefig(FIG_DIR / "weight_vs_citations.png", dpi=150)
plt.close()

# 2b. LOG-LOG REGRESSION
mask = (big["weight"] > 0) & (big["citation_sum_year"] > 0)
x = np.log10(big.loc[mask, "weight"])
y = np.log10(big.loc[mask, "citation_sum_year"])
slope, intercept, r_value, p_value, std_err = linregress(x, y)
print(f"log-log slope: {slope:.2f}, intercept: {intercept:.2f}, R^2: {r_value**2:.2f}")

plt.figure(figsize=(6, 5))
plt.scatter(x, y, alpha=0.2, label="data")
plt.plot(x, slope*x + intercept, color="red", label=f"y={slope:.2f}x+{intercept:.2f}")
plt.xlabel("log10(Weight)")
plt.ylabel("log10(Citations)")
plt.title("Log-Log Regression: Citations vs Weight")
plt.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "loglog_regression.png", dpi=150)
plt.close()

# 3. CRITICAL MASS: CITATIONS PER PAPER -------------------

big["citations_per_paper"] = np.where(big["weight"]>0, big["citation_sum_year"]/big["weight"], np.nan)

plt.figure(figsize=(6, 5))
plt.scatter(big["weight"], big["citations_per_paper"], alpha=0.2)
plt.xscale("log")
plt.yscale("log")
plt.xlabel("Weight (number of papers, log)")
plt.ylabel("Citations per paper (log)")
plt.title("Citations per paper vs Weight")
plt.tight_layout()
plt.savefig(FIG_DIR / "citation_per_paper.png", dpi=150)
plt.close()

# Optionally, plot a rolling mean to see threshold effects
weights_sorted = np.sort(big["weight"].unique())
means = [big[big["weight"]==w]["citations_per_paper"].mean() for w in weights_sorted]
plt.figure(figsize=(6, 5))
plt.plot(weights_sorted, means, marker=".")
plt.xscale("log")
plt.yscale("log")
plt.xlabel("Weight")
plt.ylabel("Avg Citations per paper")
plt.title("Mean Citations per paper vs Weight")
plt.tight_layout()
plt.savefig(FIG_DIR / "mean_citations.png", dpi=150)
plt.close()

# 4. DISTRIBUTION AND VARIANCE --------------------------

plt.figure(figsize=(6, 5))
plt.hist(big["citation_sum_year"], bins=100, log=True)
plt.xlabel("Citations per pair-year")
plt.ylabel("Frequency (log)")
plt.title("Distribution of Citations per Pair-Year")
plt.tight_layout()
plt.savefig(FIG_DIR / "distribution_of_citations.png", dpi=150)
plt.close()

var_by_pair = big.groupby("pair")["citation_sum_year"].var().dropna()
plt.figure(figsize=(6, 5))
plt.hist(var_by_pair, bins=50, log=True)
plt.xlabel("Variance of yearly citations per pair")
plt.ylabel("Number of pairs (log)")
plt.title("Variance of yearly citations across pairs")
plt.tight_layout()
plt.savefig(FIG_DIR / "variance_yearly_citations.png", dpi=150)
plt.close()

# 5. PREDICT NEXT-YEAR CITATIONS ------------------------

# Prepare data: predict next year's citations from current year's values
big = big.sort_values(["pair", "year"])
big["next_citations"] = big.groupby("pair")["citation_sum_year"].shift(-1)
train = big.dropna(subset=["next_citations", "weight", "citation_sum_year"])

X = train[["weight", "citation_sum_year"]].values
y = train["next_citations"].values

if len(train) > 100:
    model = LinearRegression().fit(X, y)
    print("\nLinear Regression to predict next-year citation_sum_year:")
    print("R^2:", model.score(X, y))
    print("Intercept:", model.intercept_)
    print("Coefficients: (weight, citation_sum_year)", model.coef_)
else:
    print("Not enough data for regression.")
