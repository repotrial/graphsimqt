import pandas as pd
import itertools as itt
from diseasomes.get_chapters_and_ranges import get_code_to_group_mapping


def compute_empirical_p_values():
    results = pd.read_csv('../results/permutation_results.csv')
    distance_types = list(set(results['distance_type']))
    comparisons = list(set(results['comparison']))
    code_to_range = get_code_to_group_mapping(comparisons, 'ranges')
    code_to_chapter = get_code_to_group_mapping(comparisons, 'chapters')
    p_values = {'comparison': [], 'distance_type': [], 'p_value': [], 'adjusted_p_value': [], 'chapter': [], 'range': []}
    num_tests = len(comparisons) - 1
    for comparison, distance_type in itt.product(comparisons, distance_types):
        distance_type_filter = results['distance_type'] == distance_type
        comparison_filter = results['comparison'] == comparison
        random_dists = list(results[distance_type_filter & comparison_filter & results['permuted']]['distance'])
        try:
            real_dist = list(results[distance_type_filter & comparison_filter & (results['permuted'] == False)]['distance'])[0]
        except KeyError:
            raise ValueError(f'comparison={comparison}, distance_type={distance_type}')
        num_smaller = 0
        for random_dist in random_dists:
            if random_dist < real_dist:
                num_smaller += 1
        p_values['comparison'].append(comparison)
        p_values['distance_type'].append(distance_type)
        p_value = (1 + num_smaller) / (len(random_dists) + 1)
        p_values['p_value'].append(p_value)
        if comparison == 'global':
            p_values['adjusted_p_value'].append(p_value)
        else:
            p_values['adjusted_p_value'].append(p_value * num_tests)
        p_values['chapter'].append(code_to_chapter[comparison])
        p_values['range'].append(code_to_range[comparison])
    p_values = pd.DataFrame(data=p_values)
    p_values.to_csv('../results/empirical_p_values.csv.bz2', index=False)


if __name__ == '__main__':
    compute_empirical_p_values()
