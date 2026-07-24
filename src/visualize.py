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