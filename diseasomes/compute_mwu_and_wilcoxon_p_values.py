import pandas as pd
import itertools as itt
import scipy.stats as sps
import argparse
from pathlib import Path
from diseasomes.utils import save_p_values


def _compute_global_or_commrocg_mwu_and_wilcoxon_p_values(result_file_prefix: str, global_or_commrocg: str):
    path_to_results = Path(f'../results/{result_file_prefix}_permutation_results.csv')
    results = pd.read_csv(str(path_to_results))
    if global_or_commrocg == 'commrocg':
        commrocg = set(pd.read_csv(str(Path('../data/commrocg.tsv')), sep='\t')['Code'])
        select_commrocg_results = results['comparison'].isin(commrocg)
        results = results[select_commrocg_results].reset_index(drop=True)
    else:
        results = results[results['comparison'] != 'global'].reset_index(drop=True)
    original = results['permuted'] == False
    permuted = results['permuted']
    distance_types = list(set(results['distance_type']))
    mwu_p_values = {'distance_type': [], 'p_value': []}
    wilcoxon_p_values = {'distance_type': [], 'p_value': []}
    for distance_type in distance_types:
        select_distance_type = results['distance_type'] == distance_type
        x = results[select_distance_type & original]['distance']
        y_mwu = results[select_distance_type & permuted]['distance']
        y_wilcoxon = results[select_distance_type & permuted].groupby('comparison').mean()['distance']
        _, mwu_p_value = sps.mannwhitneyu(x=x, y=y_mwu, alternative='less')
        _, wilcoxon_p_value = sps.wilcoxon(x=x, y=y_wilcoxon, alternative='less')
        mwu_p_values['distance_type'].append(distance_type)
        mwu_p_values['p_value'].append(mwu_p_value)
        wilcoxon_p_values['distance_type'].append(distance_type)
        wilcoxon_p_values['p_value'].append(wilcoxon_p_value)
    save_p_values(mwu_p_value, f'{result_file_prefix}_{global_or_commrocg}_mwu')
    save_p_values(mwu_p_value, f'{result_file_prefix}_{global_or_commrocg}_wilcoxon')


def _add_line_to_p_values(p_values: dict, chapter_or_range: str, group: str, distance_type: str, p_value: float,
                          num_tests: int):
    p_values[chapter_or_range].append(group)
    p_values['distance_type'].append(distance_type)
    p_values['p_value'].append(p_value)
    p_values['bonferri_adjusted_p_value'].append(p_value * num_tests)


def _compute_chapter_or_range_mwu_and_wilcoxon_p_values(result_file_prefix: str, chapter_or_range: str):
    path_to_results = Path(f'../results/{result_file_prefix}_permutation_results.csv')
    results = pd.read_csv(str(path_to_results))
    min_sample_size = 5
    distance_types = list(set(results['distance_type']))
    groups = list(set(results[chapter_or_range]))
    wilcoxon_p_values = {chapter_or_range: [], 'distance_type': [], 'p_value': [], 'bonferri_adjusted_p_value': []}
    mwu_p_values = {chapter_or_range: [], 'distance_type': [], 'p_value': [], 'bonferri_adjusted_p_value': []}
    original = results['permuted'] == False
    permuted = results['permuted']
    num_tests = 0
    for group in groups:
        select_group = results[chapter_or_range] == group
        if results[select_group & original]['distance'].shape[0] >= min_sample_size * len(distance_types):
            num_tests += 1
    for group, distance_type in itt.product(groups, distance_types):
        select_group = results[chapter_or_range] == group
        select_distance_type = results['distance_type'] == distance_type
        x = results[select_group & select_distance_type & original]['distance']
        y_mwu = results[select_group & select_distance_type & permuted]['distance']
        y_wilcoxon = results[select_group & select_distance_type & permuted].groupby('comparison').mean()['distance']
        if x.shape[0] < min_sample_size:
            continue
        try:
            _, mwu_p_value = sps.mannwhitneyu(x=x, y=y_mwu, alternative='less')
            _, wilcoxon_p_value = sps.wilcoxon(x=x, y=y_wilcoxon, alternative='less')
        except ValueError as err:
            raise ValueError(f'{err}\ngroup: {group}\ndistance_type: {distance_type}')
        _add_line_to_p_values(mwu_p_values, chapter_or_range, group, distance_type, mwu_p_value, num_tests)
        _add_line_to_p_values(wilcoxon_p_values, chapter_or_range, group, distance_type, wilcoxon_p_value, num_tests)
    save_p_values(mwu_p_value, f'{result_file_prefix}_{chapter_or_range}_mwu', chapter_or_range)
    save_p_values(mwu_p_value, f'{result_file_prefix}_{chapter_or_range}_wilcoxon', chapter_or_range)


def compute_mwu_and_wilcoxon_p_values(result_file_prefix: str):
    _compute_global_or_commrocg_mwu_and_wilcoxon_p_values(result_file_prefix, 'global')
    _compute_global_or_commrocg_mwu_and_wilcoxon_p_values(result_file_prefix, 'commrocg')
    _compute_chapter_or_range_mwu_and_wilcoxon_p_values(result_file_prefix, 'chapter')
    _compute_chapter_or_range_mwu_and_wilcoxon_p_values(result_file_prefix, 'range')


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Compute Mann-Whitney U and Wilcoxon p-values.')
    parser.add_argument('-p', type=str, required=True, help='Prefix of result file used for computing the p-values.')
    args = parser.parse_args()
    compute_mwu_and_wilcoxon_p_values(args.p)
