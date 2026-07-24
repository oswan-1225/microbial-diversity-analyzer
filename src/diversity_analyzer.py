import numpy as np
import pandas as pd

def species_richness(sample_counts: list | pd.Series) -> int:
    """
    Calculate the number of taxa present (>0 counts) in a sample.

    Parameters: 
        samples_counts: pandas Series or array of counts for one sample

    Returns:
        int: Number of taxa present in the sample with count greater than zero.
    """
    sample_counts = pd.Series(sample_counts)  # Ensure input is a pandas Series for consistency
    return np.sum(sample_counts > 0)

def shannon_diversity(sample_counts: list | pd.Series) -> float:
    """
    Calculate the Shannon diversity index for a sample.

    Parameters:
        sample_counts: pandas Series or array of counts for one sample
    Returns:
        float: Shannon diversity index for the sample.
    """
    sample_counts = pd.Series(sample_counts) # Ensure input is a pandas Series for consistency
    total_counts = sample_counts.sum()
    if total_counts == 0:
        return 0.0 # Prevents divison by zero; if no counts, diversity is 0
    proportions = sample_counts / total_counts

    # Filter out zero proportions to avoid ln(0) which is undefined
    proportions = proportions[proportions > 0]
    return -np.sum(proportions * np.log(proportions))

def summarize_diversity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes the OTU table and calculates species richness and Shannon diversity for each sample
    Then returns a new DataFrame with the results.

    Parameters:
        df: pd Dataframe containing the OTU table with samples as rows and taxa as columns. The first column should be 'group' indicating the sample group.

    Returns:
        pd.DataFrame: A new DataFrame with columns for sample ID, group, species richness, and Shannon diversity.
    """

    #Separate metadata from count data
    taxa_columns = df.columns[df.columns != 'group'] # Ignores a column named 'group' which is assumed to be the first column
    count_data = df[taxa_columns]

    richness_results = count_data.apply(species_richness, axis=1)
    shannon_results = count_data.apply(shannon_diversity, axis=1)

    # Create a new DataFrame to hold the results
    results_df = pd.DataFrame({
        'group': df['group'],
        'species_richness': richness_results,
        'shannon_diversity': shannon_results
    })
    return results_df