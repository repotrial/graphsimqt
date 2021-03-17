import pandas as pd
import itertools as itt


def summarize_empirical_p_values(group_name):
    p_values = pd.read_csv('../results/empirical_p_values.csv')
    distance_types = list(set(p_values['distance_type']))
    groups = list(set(p_values[group_name]))
    summary = {group_name: [], f'{group_name}_size': [], 'distance_type': [], 'significance_ratio': []}
    select_significant = p_values['p_value'] < 0.05
    for group, distance_type in itt.product(groups, distance_types):
        select_group = p_values[group_name] == group
        select_distance_type = p_values['distance_type'] == distance_type
        group_size = p_values[select_group & select_distance_type].shape[0]
        num_significant = p_values[select_group & select_distance_type & select_significant].shape[0]
        summary[group_name].append(group)
        summary[f'{group_name}_size'].append(group_size)
        summary['distance_type'].append(distance_type)
        summary['significance_ratio'].append(num_significant / group_size)
    summary = pd.DataFrame(data=summary)
    summary.to_csv(f'../results/empirical_p_values_{group_name}_summary.csv', index=False)


if __name__ == '__main__':
    summarize_empirical_p_values('chapter')
    summarize_empirical_p_values('range')
