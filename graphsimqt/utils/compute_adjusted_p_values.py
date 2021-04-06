from statsmodels.stats.multitest import multipletests
import pandas as pd


def compute_adjusted_p_values(p_values: pd.DataFrame, adjust_method: str):
    p_values['adjusted_p_value'] = [None for _ in range(p_values.shape[0])]
    distance_types = list(set(p_values['distance_type']))
    for distance_type in distance_types:
        selection = p_values['distance_type'] == distance_type
        original_p_values = p_values.loc[selection, 'p_value'].to_numpy()
        _, adjusted_p_values, _, _ = multipletests(original_p_values, method=adjust_method)
        p_values.loc[selection, 'adjusted_p_value'] = adjusted_p_values