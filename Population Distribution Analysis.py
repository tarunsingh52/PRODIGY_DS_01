import glob
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------
DATA_DIR = "data"
OUTPUT_DIR = "output"
YEAR = "2024"          # most recent complete year in the dataset
TOP_N = 15             # how many countries to show in the bar chart

# A small, professional colour palette used across every chart
COLOR_MAIN = "#2E5EAA"
COLOR_ACCENT = "#F2A541"
COLOR_GRID = "#DDDDDD"

plt.rcParams.update({
    "font.size": 11,
    "axes.edgecolor": "#444444",
    "axes.labelcolor": "#222222",
    "text.color": "#222222",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


# ----------------------------------------------------------------------
# 1. LOAD
# ----------------------------------------------------------------------
def find_file(pattern):
    """Find a data file in DATA_DIR matching a glob pattern.

    Using a pattern (instead of a hard-coded file name) means the script
    still works if the CSV is re-downloaded from World Bank in future and
    gets a different numeric suffix in its file name.
    """
    matches = glob.glob(os.path.join(DATA_DIR, pattern))
    if not matches:
        sys.exit(
            f"Could not find a file matching '{pattern}' inside '{DATA_DIR}/'.\n"
            f"Make sure the World Bank CSV files are placed in the data/ folder."
        )
    return matches[0]


def load_population_data():
    """Load the main World Bank population CSV (skips 4 metadata rows)."""
    path = find_file("API_SP.POP.TOTL*.csv")
    df = pd.read_csv(path, skiprows=4)
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]  # drop trailing blank column
    return df


def load_country_metadata():
    """Load the World Bank country metadata CSV (Region / Income Group)."""
    path = find_file("Metadata_Country_API_SP.POP.TOTL*.csv")
    meta = pd.read_csv(path)
    meta = meta.loc[:, ~meta.columns.str.startswith("Unnamed")]
    return meta


# ----------------------------------------------------------------------
# 2. CLEAN
# ----------------------------------------------------------------------
def clean_and_merge(pop_df, meta_df):
    """Merge population data with metadata and drop non-country aggregates.

    The World Bank file includes rows like "World", "High income" and
    "East Asia & Pacific" alongside real countries. Rows for those
    aggregates always have an empty 'Region' in the metadata file, while
    every genuine country has a Region assigned. Filtering on that column
    is a reliable way to keep individual countries only.
    """
    merged = pop_df.merge(meta_df[["Country Code", "Region", "IncomeGroup"]],
                           on="Country Code", how="left")
    countries_only = merged[merged["Region"].notna()].copy()
    countries_only[YEAR] = pd.to_numeric(countries_only[YEAR], errors="coerce")
    countries_only = countries_only.dropna(subset=[YEAR])
    return countries_only


# ----------------------------------------------------------------------
# Helper: format big numbers as 1.4B / 340M / 12K for axis labels
# ----------------------------------------------------------------------
def human_format(num, _pos=None):
    for unit, div in [("B", 1e9), ("M", 1e6), ("K", 1e3)]:
        if abs(num) >= div:
            return f"{num / div:.1f}{unit}"
    return f"{num:.0f}"


# ----------------------------------------------------------------------
# 3a. BAR CHART - Top N most populous countries (categorical variable)
# ----------------------------------------------------------------------
def plot_top_countries_bar(df, save_path):
    top = df.nlargest(TOP_N, YEAR).sort_values(YEAR, ascending=True)

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = [COLOR_ACCENT if i == len(top) - 1 else COLOR_MAIN
              for i in range(len(top))]
    bars = ax.barh(top["Country Name"], top[YEAR], color=colors)

    for bar, value in zip(bars, top[YEAR]):
        ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
                human_format(value), va="center", fontsize=9.5)

    ax.set_title(f"Top {TOP_N} Most Populous Countries ({YEAR})",
                 fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("Population")
    ax.set_ylabel("")
    ax.set_xlim(0, top[YEAR].max() * 1.16)  # headroom so value labels never clip
    ax.xaxis.set_major_formatter(plt.FuncFormatter(human_format))
    ax.grid(axis="x", color=COLOR_GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    fig.tight_layout()
    fig.savefig(save_path, dpi=200)
    plt.close(fig)
    print(f"Saved: {save_path}")


# ----------------------------------------------------------------------
# 3b. HISTOGRAM - Population distribution across every country (continuous)
# ----------------------------------------------------------------------
def plot_population_histogram(df, save_path):
    values = df[YEAR].values
    # Population is extremely right-skewed (most countries are small,
    # a handful like India/China/USA are huge), so log-spaced bins give
    # a far more informative picture than evenly-spaced linear bins.
    bins = np.logspace(np.log10(values.min()), np.log10(values.max()), 25)

    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.hist(values, bins=bins, color=COLOR_MAIN, edgecolor="white", alpha=0.9)
    ax.set_xscale("log")

    mean_val, median_val = values.mean(), np.median(values)
    ax.axvline(mean_val, color=COLOR_ACCENT, linestyle="--", linewidth=2,
               label=f"Mean: {human_format(mean_val)}")
    ax.axvline(median_val, color="#5A5A5A", linestyle=":", linewidth=2,
               label=f"Median: {human_format(median_val)}")

    ax.set_title(f"Distribution of Country Population Sizes ({YEAR})",
                 fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("Population (log scale)")
    ax.set_ylabel("Number of Countries")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(human_format))
    ax.grid(axis="y", color=COLOR_GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(frameon=False)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    fig.tight_layout()
    fig.savefig(save_path, dpi=200)
    plt.close(fig)
    print(f"Saved: {save_path}")


# ----------------------------------------------------------------------
# 3c. BAR CHART - Number of countries per region (categorical variable)
# ----------------------------------------------------------------------
def plot_region_bar_chart(df, save_path):
    counts = df["Region"].value_counts().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(counts.index, counts.values, color=COLOR_MAIN)
    for bar, value in zip(bars, counts.values):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                str(value), va="center", fontsize=10)

    ax.set_title("Number of Countries per World Bank Region",
                 fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("Number of Countries")
    ax.set_xlim(0, counts.values.max() * 1.15)  # headroom so value labels never clip
    ax.grid(axis="x", color=COLOR_GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    fig.tight_layout()
    fig.savefig(save_path, dpi=200)
    plt.close(fig)
    print(f"Saved: {save_path}")


# ----------------------------------------------------------------------
# 4. SUMMARY
# ----------------------------------------------------------------------
def print_summary(df):
    values = df[YEAR]
    print(f"\n----- SUMMARY STATISTICS ({YEAR}, countries only) -----")
    print(f"Countries analysed : {len(df)}")
    print(f"Total population   : {human_format(values.sum())}")
    print(f"Mean population    : {human_format(values.mean())}")
    print(f"Median population  : {human_format(values.median())}")
    print(f"Largest country    : {df.loc[values.idxmax(), 'Country Name']} "
          f"({human_format(values.max())})")
    print(f"Smallest country   : {df.loc[values.idxmin(), 'Country Name']} "
          f"({human_format(values.min())})")
    print("-" * 55)


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    pop_df = load_population_data()
    meta_df = load_country_metadata()
    clean_df = clean_and_merge(pop_df, meta_df)

    plot_top_countries_bar(
        clean_df, os.path.join(OUTPUT_DIR, "top_15_countries_bar_chart.png"))
    plot_population_histogram(
        clean_df, os.path.join(OUTPUT_DIR, "population_distribution_histogram.png"))
    plot_region_bar_chart(
        clean_df, os.path.join(OUTPUT_DIR, "countries_per_region_bar_chart.png"))

    print_summary(clean_df)
    print(f"\nAll charts saved inside the '{OUTPUT_DIR}/' folder.")


if __name__ == "__main__":
    main()
