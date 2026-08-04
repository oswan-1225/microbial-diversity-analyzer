import numpy as np
import pandas as pd

def species_richness(sample_counts: list | pd.Series, threshold: float = 0.0) -> int:
    """
    Calculate the number of taxa present (above threshold) in a sample.

    Parameters:
        sample_counts: pandas Series or array of counts/abundances for one sample
        threshold: minimum value for a taxon to be considered "present".
            Default 0.0 preserves original behavior (any nonzero count).
            For relative-abundance data, consider a small positive value
            (e.g. 0.0001) to exclude noise-level detections.

    Returns:
        int: number of taxa with value > threshold
    """
    sample_counts = pd.Series(sample_counts)
    return np.sum(sample_counts > threshold)

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

def summarize_diversity(df: pd.DataFrame, group_col: str = 'group', exclude_cols: list | None = None, richness_threshold: float = 0.0) -> pd.DataFrame:
    """
    Takes the OTU table and calculates species richness and Shannon diversity for each sample
    Then returns a new DataFrame with the results.

    Parameters:
        df: pd Dataframe containing the OTU table with samples as rows and taxa as columns. The first column should be 'group' indicating the sample group.
        group_col: The name of the column containing the group information. Default is 'group'.
        exclude_cols: List of columns to exclude from the diversity calculations (e.g., metadata columns). Default is None.
        Richness_threshold: mnimum value for a taxon to count as "present" in the species_richness calculation. Default is 0.0 use a psmall positive value for relative-abundance data to exclude noise-level detections.

    Returns:
        pd.DataFrame: A new DataFrame with columns for sample ID, group, species richness, and Shannon diversity.
    """
    if exclude_cols is None:
        exclude_cols = []

    #Separate metadata from count data
    non_taxa_cols = [group_col] + exclude_cols
    taxa_columns = df.columns[~df.columns.isin(non_taxa_cols)] # Ignores a column named 'group' which is assumed to be the first column
    count_data = df[taxa_columns]

    richness_results = count_data.apply(lambda row: species_richness(row, threshold=richness_threshold), axis=1)
    shannon_results = count_data.apply(shannon_diversity, axis=1)

    # Create a new DataFrame to hold the results
    summary_df = pd.DataFrame({
        group_col: df[group_col],
        'species_richness': richness_results,
        'shannon_diversity': shannon_results
    })
    return summary_df