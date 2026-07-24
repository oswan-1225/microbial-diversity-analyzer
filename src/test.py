from diversity_analyzer import summarize_diversity
from visualize import diversity_boxplot
import pandas as pd

df = pd.read_csv("data/raw/fake_otu_table.csv", index_col=0)
summary = summarize_diversity(df)
diversity_boxplot(summary, metric="species_richness", save_path="results_species_richness_boxplot.png")