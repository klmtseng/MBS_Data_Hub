import pandas as pd

def calculate_spread(df: pd.DataFrame, series1_code: str, series2_code: str) -> pd.DataFrame:
    """
    Calculates the spread between two series in a DataFrame.

    Args:
        df: The input DataFrame.
        series1_code: The code for the first series.
        series2_code: The code for the second series.

    Returns:
        The DataFrame with a new column for the spread.
    """
    spread_name = f"{series1_code}-{series2_code}_Spread"
    df[spread_name] = df[series1_code] - df[series2_code]
    return df
