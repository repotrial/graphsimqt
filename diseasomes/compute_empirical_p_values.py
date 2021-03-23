import pandas as pd
import itertools as itt
from diseasomes.utils import get_code_to_group_mapping, save_p_values
from pathlib import Path
import argparse


def compute_empirical_p_values(result_file_prefix: str):
    path_to_results = Path(f'../results/{result_file_prefix}_permutation_results.csv')
    results = pd.read_csv(str(path_to_results))
    distance_types = list(set(results['distance_type']))
    comparisons = list(set(results['comparison']))
    code_to_range = get_code_to_group_mapping(comparisons, 'ranges')
    code_to_chapter = get_code_to_group_mapping(comparisons, 'chapters')
    p_values = {'comparison': [], 'distance_type': [], 'p_value': [], 'bonferri_adjusted_p_value': [],
                'benjamini_hochberg_adjusted_p_value': [], 'chapter': [], 'range': []}
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
            p_values['bonferri_adjusted_p_value'].append(p_value)
        else:
            p_values['bonferri_adjusted_p_value'].append(p_value * num_tests)
        p_values['chapter'].append(code_to_chapter[comparison])
        p_values['range'].append(code_to_range[comparison])
        p_values['benjamini_hochberg_adjusted_p_value'].append(None)
    p_values = pd.DataFrame(data=p_values)
    global_p_values = p_values[p_values['comparison'] == 'global'].reset_index(drop=True)
    disease_p_values = p_values[p_values['comparison'] != 'global'].reset_index(drop=True)
    disease_p_values.rename(columns={'comparison': 'disease'})
    save_p_values(global_p_values, f'{result_file_prefix}_global_empirical')
    save_p_values(disease_p_values, f'{result_file_prefix}_disease_empirical', 'disease')


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Compute empirical p-values.')
    parser.add_argument('-p', type=str, required=True, help='Prefix of result file used for computing the p-values.')
    args = parser.parse_args()
    compute_empirical_p_values(args.p)
