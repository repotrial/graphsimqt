import pandas as pd
import scipy.stats as sps


def analyze_commrocg():
    p_values = pd.read_csv('../results/empirical_p_values.csv')
    results = pd.read_csv('../results/permutation_results.csv')
    commrocg = set(pd.read_csv('../data/commrocg.tsv', sep='\t')['Code'])
    select_commrocg_p_values = p_values['comparison'].isin(commrocg)
    select_commrocg_results = results['comparison'].isin(commrocg)
    distance_types = list(set(p_values['distance_type']))
    select_significant = p_values['p_value'] < 0.05
    commrocg_results = {'distance_type': [], 'significance_ratio': [], 'significant_diseases': [], 'p_value': []}
    original = results['permuted'] == False
    permuted = results['permuted']
    for distance_type in distance_types:
        select_distance_type_p_values = p_values['distance_type'] == distance_type
        select_distance_type_results = results['distance_type'] == distance_type
        significant_diseases = p_values[select_significant & select_commrocg_p_values & select_distance_type_p_values]
        num_significant = significant_diseases.shape[0]
        significant_diseases = ';'.join(list(significant_diseases['comparison']))
        x = results[select_commrocg_results & select_distance_type_results & original]['distance']
        y = results[select_commrocg_results & select_distance_type_results & permuted]['distance']
        _, p_value = sps.mannwhitneyu(x=x, y=y, alternative='less')
        commrocg_results['distance_type'].append(distance_type)
        commrocg_results['significance_ratio'].append(num_significant / len(commrocg))
        commrocg_results['significant_diseases'].append(significant_diseases)
        commrocg_results['p_value'].append(p_value)
    commrocg_results = pd.DataFrame(data=commrocg_results)
    commrocg_results.to_csv('../results/commrocg_results.csv', index=False)


if __name__ == '__main__':
    analyze_commrocg()
