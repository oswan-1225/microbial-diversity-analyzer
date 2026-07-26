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

def compare_multiple_groups(summary_df: pd.DataFrame, metric: str, control_label: str, group_col: str = "group") -> pd.DataFrame:
    """
    Function that allows for the comparison of any number of "treatment" groups 
    with the "control" group using the Mann-Whitney U test.
    """

    ### defines all groups vs the treatment groups
    all_groups = summary_df[group_col].unique()
    treatment_groups = [group for group in all_groups if group != control_label]

    # Iterates through each treatment group and compares it to the control group using the compare_groups function
    results = []
    for treatment_group in treatment_groups:
        subset = summary_df[summary_df[group_col].isin([control_label, treatment_group])]
        result = compare_groups(subset, metric, group_col)
        results.append({'treatment': treatment_group, 'statistic': result['statistic'], 'p_value': result['p_value']})

    # Bonferroni correction for multiple comparisons
    num_comparisons = len(treatment_groups)
    for i in range(len(results)):
        results[i]['corrected_p_value'] = min(results[i]['p_value'] * num_comparisons, 1.0)
        results[i]['significant'] = results[i]['corrected_p_value'] < 0.05

    return pd.DataFrame(results)