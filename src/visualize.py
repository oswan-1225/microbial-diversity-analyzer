import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Optional

def diversity_boxplot(df: pd.DataFrame, metric: str, save_path: Optional[str] = None) -> None:
    """
    Create a boxplot for the specified diversity metric.

    Parameters:
        df: pd.DataFrame containing the diversity metrics including a 'group' column
        metric: str, the column name of the diversity metric
        save_path: str, optional path to save the plot. If None, the plot will be displayed.
    """
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='group', y=metric)
    sns.stripplot(data=df, x='group', y=metric, color='black', alpha=0.5, jitter=True)

    plt.title(f"{metric.replace('_', ' ').title()} by Group")
    plt.xlabel('Group')
    plt.ylabel(metric.replace('_', ' ').title())
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Boxplot saved to {save_path}")
    else:
        plt.show()

def p_value_to_asterisks(p_value: float) -> str:
    """
    Convert a p-value to a string of asterisks for significance annotation.

    Parameters:
        p_value: float, the p-value to convert
    
    Returns:
        str: A string of asterisks representing significance level
    """
    if p_value < 0.001:
        return '***'
    elif p_value < 0.01:
        return '**'
    elif p_value < 0.05:
        return '*'
    else:
        return 'ns'  # Not significant

def multi_group_boxplot(summary_df: pd.DataFrame, stats_df: pd.DataFrame, metric: str, control_label: str, group_col: str = "group", save_path: Optional[str] = None, richness_threshold: Optional[float] = None) -> None:

    """
    Creates a boxplot of all groups with p value annotations
    """

    plt.figure(figsize=(10, 6))
    ax = sns.boxplot(data=summary_df, x=group_col, y=metric)
    sns.stripplot(data=summary_df, x=group_col, y=metric, color='black', alpha=0.5, jitter=True)

    # Gets L to R order of the groups on the x-axis
    group_order = [label.get_text() for label in ax.get_xticklabels()]

    # Computes the starting height for the annotations, above the tallest data point
    y_max = summary_df[metric].max()
    y_step = (y_max - summary_df[metric].min()) * 0.1 # spacing between annotations
    current_height = y_max + y_step

    # Find the index of the control group in the order
    control_x = group_order.index((str(control_label)))

    for _, row in stats_df.iterrows():
        treatment_x = group_order.index(str(row['treatment']))
        asterisks = p_value_to_asterisks(row['corrected_p_value'])

        x1, x2 = control_x, treatment_x
        y = current_height
        h = y_step * 0.2 

        plt.plot([x1, x1, x2, x2], [y, y+h, y+h, y], color='black')
        plt.text((x1 + x2) * 0.5, y + h, f"{asterisks}\np={row['corrected_p_value']:.4f}", ha='center', va='bottom', fontsize=9)

        current_height += y_step 

    title = f"{metric.replace('_', ' ').title()} by Group"
    if metric == "species_richness" and richness_threshold is not None:
        title += f" (Threshold > {richness_threshold})"

    plt.title(title)
    plt.xlabel('Group')
    plt.ylabel(metric.replace('_', ' ').title())
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Boxplot saved to {save_path}")
    else:
        plt.show()