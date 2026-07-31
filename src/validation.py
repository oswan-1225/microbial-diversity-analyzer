import pandas as pd

def validate_input_data(df: pd.DataFrame, group_col: str, control_label: str, exclude_cols: list | None = None) -> None:
    """
    Validates the assumptions about a loaded OTU table.
    Raises ValueError immediately if requirements are violated.
    These are checks with no reasonable default
    """
    if exclude_cols is None:
        exclude_cols = []

    # First check: group_col exists
    if group_col not in df.columns:
        raise ValueError(f"'{group_col}' column is missing from the DataFrame.")

    # Second check: control_label exists as values in group_col
    unique_groups = df[group_col].unique()
    if control_label not in unique_groups:
        raise ValueError(f"'{control_label}' is not present in the '{group_col}' column. Found groups: {unique_groups}")

    # Third check: at least 2 groups present
    if len(unique_groups) < 2:
        raise ValueError(f"At least two groups are required in the '{group_col}' column. Found only: {unique_groups}")

    if exclude_cols is None:
        exclude_cols = []

    # Remaining checks operate on count/taxa columns only
    non_taxa_cols = [group_col] + exclude_cols
    taxa_columns = df.columns[~df.columns.isin(non_taxa_cols)]
    count_data = df[taxa_columns]

    # Fourth check: all count columns are numeric
    non_numeric = count_data.select_dtypes(exclude='number').columns.tolist()
    if non_numeric:
        raise ValueError(f"The following count columns are not numeric: {list(non_numeric)}")

    # Fifth check: no negative counts
    if (count_data < 0).values.any():
        bad_cols = count_data.columns[(count_data < 0).any()].tolist()
        raise ValueError(f"Negative counts found in the following columns: {bad_cols}")

def check_missing_values(count_data: pd.DataFrame, on_missing: str = 'error') -> pd.DataFrame:
    """
    Handles NaN values in the count data.
    Missing data is ambiguous so the caller must choose how to handle it.
    
    Parameters:
        count_data: Dataframe of numeric count columns (no group/metadata columns)
        on_missing: 'error' (default, refuse to proceed, 'fill_zero' or 'drop_rows')
        
    Returns:
        pd.Dataframe
    """
    if not count_data.isnull().values.any():
        return count_data #nothing missing

    bad_cols = count_data.columns[count_data.isnull().any()].tolist()
    n_missing = count_data.isnull().values.sum()

    if on_missing == 'error':
        raise ValueError(
            f"Found {n_missing} missing values in columns: {bad_cols}"
            f"Pass on_missing='fill_zero' or on_missing='drop_rows' to handle automatically."  
        )
    elif on_missing == 'fill_zero':
        print(f"Warning: filling {n_missing} values with 0 in columns: {bad_cols}")
        return count_data.fillna(0)
    
    elif on_missing == 'drop_rows':
        before = len(count_data)
        count_data = count_data.dropna()
        print(f"Warning: dropped {before - len(count_data)} rows containing missing values in columns: {bad_cols}")
        return count_data

    else:
        raise ValueError(f"Invalid value for on_missing: {on_missing}. Must be 'error', 'fill_zero', or 'drop_rows'.")
