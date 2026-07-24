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