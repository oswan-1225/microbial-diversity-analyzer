import numpy as np
import pandas as pd

np.random.seed(42)  # For reproducibility

n_taxa = 60

group_sizes = {
    'control': 10,
    'antibiotic': 8,
    'antifungal': 6,
    'heat_stress': 12
}

taxa_names = [f'Taxon_{i+1}' for i in range(n_taxa)]

# Build sample IDs and matching group labels for uneven group sizes
sample_ids = []
group_labels = []
for group, size in group_sizes.items():
    for i in range(size):
        sample_ids.append(f'{group}_{i:02d}')
        group_labels.append(group)

n_samples = len(sample_ids)

# generate random count data using a negative binomial distribution
data = np.random.negative_binomial(n=5, p=0.5, size=(n_samples, n_taxa))
df = pd.DataFrame(data, index=sample_ids, columns=taxa_names)
df.insert(0, 'group', group_labels)

# Treatments

#Antibiotic: knocks down a specific set of taxa (first 15), meant to reduce overall bacterial diversity - a "should be significant" case
antibiotoics_sensitive = taxa_names[:15]
antiobiotic_mask = df['group'] == 'antibiotic'
for taxon in antibiotoics_sensitive:
    df.loc[antiobiotic_mask, taxon] = (df.loc[antiobiotic_mask, taxon] * 0.15).astype(int)

# Antifungal: knocks down a totally different set of taxa (last 10),
# meant to barely affect overall bacterial diversity - a "should be non-significant" case
antifungal_sensitive = taxa_names[-10:]
antifungal_mask = df["group"] == "antifungal"
for taxon in antifungal_sensitive:
    df.loc[antifungal_mask, taxon] = (df.loc[antifungal_mask, taxon] * 0.5).astype(int)

# Heat stress: broad mild reduction across MANY taxa (different pattern - overall stress, not targeted)
heat_mask = df["group"] == "heat_stress"
heat_affected = taxa_names[10:50]  # a large swath, but each only mildly reduced
for taxon in heat_affected:
    df.loc[heat_mask, taxon] = (df.loc[heat_mask, taxon] * 0.7).astype(int)

df.to_csv('data/raw/fake_data.csv', index=True)
print(df.shape)
print(df['group'].value_counts())
print(df.head())