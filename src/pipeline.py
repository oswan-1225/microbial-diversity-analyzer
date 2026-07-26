import pandas as pd
import os
from typing import Optional
from diversity_analyzer import summarize_diversity
from stats_tests import compare_multiple_groups
from visualize import multi_group_boxplot

def run_pipeline(input_path: str, output_dir: str, control_label: str, group_col: str = 'group', metrics: Optional[list] = None) -> dict:
    '''
    Runs a full pipeline analysis for a single statistical test comparing a control group to multiple treatment groups.
    
    Parameters:
        input_path: str, path to the input CSV file containing the OTU table with samples as rows and taxa as columns. The first column should be a group column indicating the sample type
        output_dir: str, path to the directory where output files will be saved.
        control_label: str, label of the control group in the 'group' column.
        group_col: str, name of the column containing group labels. Default is 'group'.
        metrics: list of str, names of the diversity metrics to analyze. Default is ['species_richness', 'shannon_diversity'].
    
    Returns:
        dict: A dictionary containing the summary DataFrame, statistical results DataFrame, and paths to saved plots.
    '''

    if metrics is None:
        metrics = ['species_richness', 'shannon_diversity'] # Leaves open space for future metrics to be added

    df = pd.read_csv(input_path, index_col = 0) # reads the input CSV file into a DataFrame, using the first column as the index (sample IDs)
    os.makedirs(output_dir, exist_ok=True) # Creates the output directory if it doesn't exist

    summary = summarize_diversity(df, group_col=group_col)
    summary.to_csv(os.path.join(output_dir, 'summarized_data.csv'), index=False) # Saves the summarized diversity data to a CSV file

    all_stats = {}
    for metric in metrics:
        stats_results = compare_multiple_groups(summary, metric=metric, control_label=control_label, group_col=group_col)

        plot_path = os.path.join(output_dir, f"{metric}_boxplot.png")
        multi_group_boxplot(summary, stats_results, metric=metric, control_label=control_label, group_col=group_col, save_path=plot_path)

        stats_results.to_csv(os.path.join(output_dir, f"{metric}_stats_results.csv"), index=False) # Saves the statistical results to a CSV file
        all_stats[metric] = stats_results

    return {'summary': summary, 'stats': all_stats, 'plots': {metric: os.path.join(output_dir, f"{metric}_boxplot.png") for metric in metrics}}