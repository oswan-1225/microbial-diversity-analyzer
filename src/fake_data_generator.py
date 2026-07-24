import numpy as np
import pandas as pd
from polars import groups
from polars import groups

# Generate fake OTU table data

np.random.seed(42) # Reproducibility

n_samples = 20 # Rows 
n_taxa = 15 #Columns

# Samples names

sample_ids = [f"sample_{i:02d}" for i in range(n_samples)]
taxa_names = [f"taxon_{i:02d}" for i in range(n_taxa)]

# Groups: first half are control, second half are treated
groups = ["control"] * (n_samples // 2) + ["treated"] * (n_samples // 2)

# Abundance data: random counts from a negative binomial distribution to simulate overdispersion
data = np.random.negative_binomial(n=5, p=0.3, size=(n_samples, n_taxa))

df = pd.DataFrame(data, index=sample_ids, columns=taxa_names)
df.insert(0, "group", groups)

# microbial effect simulation: randomly impact some of the taxa in the treated group
effected_taxa = taxa_names[:5]  # First 5 taxa are negatively impacted in the treated group
treated_mask = df['group'] == 'treated'
for taxon in effected_taxa:
    df.loc[treated_mask, taxon] = (df.loc[treated_mask, taxon] * 0.2).astype(int)  # Reduce counts by 80% for treated group

# Save to CSV
df.to_csv('data/raw/fake_otu_table.csv')
print(df.head())
print(f"\nSaved {df.shape[0]} samples and {df.shape[1]-1} taxa to 'data/raw/fake_otu_table.csv'.")