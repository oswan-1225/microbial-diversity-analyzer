from scipy import stats
import pandas as pd

def compare_groups(summary_df: pd.DataFrame, metric: str, group_col: str = "group") -> dict:
    """
    Run a Mann-Whitney U test comparing a metric between two groups.

    Parameters:
        summary_df: DataFrame containing at least [group_col, metric]
        metric: name of the column to compare
        group_col: name of the column containing group labels

    Returns:
        dict with keys: group_a, group_b, statistic, p_value
    """
    # Finds the unique group labels in the specified column
    group_labels = summary_df[group_col].unique()

    # Mann-Whitney U test requires 2 groups, so we check if there are exactly 2 unique groups
    if len(group_labels) != 2:
        raise ValueError("compare_groups requires exactly 2 groups, found: {}".format(len(group_labels)))

    # Finds the values for each group a and b
    group_a_values = summary_df[summary_df[group_col] == group_labels[0]][metric]
    group_b_values = summary_df[summary_df[group_col] == group_labels[1]][metric]

    # the Mann-Whitney U test is performed on the specified metric for both groups
    stat, p_value = stats.mannwhitneyu(group_a_values, group_b_values, alternative='two-sided')

    # returns a dictionary containing the group labels, the test statistic, and the p-value
    return {
        "group_a": group_labels[0],
        "group_b": group_labels[1],
        "statistic": stat,
        "p_value": p_value
    }