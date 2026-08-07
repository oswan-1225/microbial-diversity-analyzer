import pandas as pd

def apply_relabeling(df: pd.DataFrame, column: str, mapping: dict) -> pd.DataFrame:
    """
    Replace values in a column according to a provided mapping.
    Values not present in the mapping are left unchanged.

    Parameters:
        df: DataFrame to modify
        column: name of the column to relabel
        mapping: dict of {old_value: new_value}

    Returns:
        pd.DataFrame with the column relabeled
    """
    df[column] = df[column].replace(mapping)
    return df

def parse_relabel_arg(relabel_str: str) -> tuple[str, dict]:
    """
    Parse a CLI relabel string like 'Diet:0=LFPP,1=Western' into
    (column_name, {old: new, ...}). Numeric-looking keys are converted
    to int so they match numeric columns correctly.
    """
    column, pairs_str = relabel_str.split(":", 1)
    mapping = {}
    for pair in pairs_str.split(","):
        old, new = pair.split("=", 1)
        try:
            old = int(old)
        except ValueError:
            pass  # keep as string if it's not a valid integer
        mapping[old] = new
    return column, mapping