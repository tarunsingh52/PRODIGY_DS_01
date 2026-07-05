# 📊 Population Distribution Visualization

Visualizing the distribution of a **continuous variable** (population size) and a
**categorical variable** (country / region) using official World Bank data.

## Task

> Create a bar chart or histogram to visualize the distribution of a categorical
> or continuous variable, such as the distribution of ages or genders in a population.

## 📁 Dataset

- **Source:** [World Bank Open Data — Population, total (SP.POP.TOTL)](https://data.worldbank.org/indicator/SP.POP.TOTL)
- **Coverage:** 217 countries, 1960–2024
- Files (in `data/`):
  - `API_SP.POP.TOTL_DS2_en_csv_v2_38144.csv` — population by country & year
  - `Metadata_Country_API_SP.POP.TOTL_DS2_en_csv_v2_38144.csv` — region & income group per country

## ⚙️ What the script does

1. **Loads** the raw World Bank export.
2. **Cleans** it — the raw file mixes real countries together with aggregate
   rows such as `World`, `High income`, and `East Asia & Pacific`. These are
   detected and removed using the country metadata file, leaving 217 genuine
   countries.
3. **Generates three charts**, saved automatically to `output/`:

   | Chart | Type | Variable |
   |---|---|---|
   | Top 15 most populous countries | Bar chart | Categorical (country) |
   | Population size distribution | Histogram (log scale) | Continuous (population) |
   | Countries per region | Bar chart | Categorical (region) |

4. **Prints summary statistics** (mean, median, largest/smallest country, etc.) to the console.

## 📈 Output

### Top 15 Most Populous Countries (2024)
![Top 15 most populous countries](output/top_15_countries_bar_chart.png)

### Distribution of Population Sizes Across All Countries
![Population distribution histogram](output/population_distribution_histogram.png)

### Number of Countries per World Bank Region
![Countries per region](output/countries_per_region_bar_chart.png)

## ▶️ How to run

```bash
pip install -r requirements.txt
python population_distribution_analysis.py
```

Charts are (re)generated inside the `output/` folder and a summary prints to the console.

## 💡 Key insight

Population size across countries is **heavily right-skewed**: the median
country has around 6.6M people, while a small handful — India, China, the
United States — hold hundreds of millions to over a billion. That's why the
histogram uses a **log scale**: on a normal scale, nearly every country would
be crushed into a single bar next to India and China, hiding the real shape
of the distribution.

## 🛠️ Tech stack

- Python 3
- pandas
- matplotlib
- numpy

## 📂 Project structure

```
.
├── population_distribution_analysis.py   # main script
├── requirements.txt
├── data/                                 # raw World Bank CSVs
└── output/                               # generated charts (PNG)
```
