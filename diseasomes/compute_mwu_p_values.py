import pandas as pd
import itertools as itt
import scipy.stats as sps


def compute_mwu_p_values(group_name):
    results = pd.read_csv('../results/permutation_results.csv')
    distance_types = list(set(results['distance_type']))
    groups = list(set(results[group_name]))
    p_values = {group_name: [], 'distance_type': [], 'p_value': []}
    for group, distance_type in itt.product(groups, distance_types):
        select_group = results[group_name] == group
        select_distance_type = results['distance_type'] == distance_type
        original = results['permuted'] == False
        permuted = results['permuted']
        x = results[select_group & select_distance_type & original]['distance']
        y = results[select_group & select_distance_type & permuted]['distance']
        if x.shape[0] < 20:
            continue
        try:
            _, p_value = sps.mannwhitneyu(x=x, y=y, alternative='less')
        except ValueError as err:
            raise ValueError(f'{err}\ngroup: {group}\ndistance_type: {distance_type}')
        p_values[group_name].append(group)
        p_values['distance_type'].append(distance_type)
        p_values['p_value'].append(p_value)
    p_values = pd.DataFrame(data=p_values)
    p_values.to_csv(f'../results/mwu_{group_name}_p_values.csv', index=False)


if __name__ == '__main__':
    compute_mwu_p_values('chapter')
    compute_mwu_p_values('range')
