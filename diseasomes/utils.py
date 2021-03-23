import pandas as pd
from pathlib import Path
import argparse


def _in_code_range(code_range, code):
    start, end = code_range.split('-')
    return start <= code <= end


def _find_chapter(chapters, code):
    for row in range(chapters.shape[0]):
        if _in_code_range(chapters.loc[row, 'Code Range'], code):
            return chapters.loc[row, 'Chapter'], chapters.loc[row, 'Description']


def _find_range(ranges, code):
    for row in range(ranges.shape[0]):
        if _in_code_range(ranges.loc[row, 'Code Range'], code):
            return ranges.loc[row, 'Range'], ranges.loc[row, 'Description']


def _compute_benjamini_hochberg_p_values(p_values, benjamini_hochberg_column):
    p_values['benjamini_hochberg_adjusted_p_value'] = [None for _ in range(p_values.shape[0])]
    tests = list(set(p_values[benjamini_hochberg_column]))
    distance_types = list(set(p_values['distance_type']))
    benjamini_hochberg_p_values = pd.DataFrame(index=tests, columns=distance_types)
    for distance_type in distance_types:
        p_values_for_distance_type = p_values[p_values['distance_type'] == distance_type]
        p_values_for_distance_type.sort_values(by=[benjamini_hochberg_column], inplace=True)
        p_values_for_distance_type.reset_index(drop=True, inplace=True)
        previous_test = None
        for rank in range(p_values_for_distance_type.shape[0], 0, -1):
            test = p_values_for_distance_type.loc[rank - 1, benjamini_hochberg_column]
            adjusted_p_value = p_values_for_distance_type.loc[rank - 1, 'bonferri_adjusted_p_value'] / rank
            if previous_test is not None:
                adjusted_p_value = min(adjusted_p_value, benjamini_hochberg_p_values.loc[previous_test, distance_type])
            benjamini_hochberg_p_values.loc[test, distance_type] = min(adjusted_p_value, 1)
            previous_test = test
    for i in range(p_values.shape[0]):
        test = p_values.loc[i, benjamini_hochberg_column]
        distance_type = p_values.loc[i, 'distance_type']
        p_values.loc[i, 'benjamini_hochberg_adjusted_p_value'] = benjamini_hochberg_p_values.loc[test, distance_type]


def get_code_to_group_mapping(codes, group_type):
    groups = pd.read_csv(str(Path(f'../data/icd10_{group_type}.tsv')), sep='\t')
    codes_to_groups = {}
    for code in codes:
        if code == 'global':
            codes_to_groups[code] = 'Global'
        elif group_type == 'chapters':
            codes_to_groups[code] = _find_chapter(groups, code)
        else:
            codes_to_groups[code] = _find_range(groups, code)
    return codes_to_groups


def save_p_values(p_values, prefix, benjamini_hochberg_column=None):
    p_values = pd.DataFrame(p_values)
    if benjamini_hochberg_column:
        _compute_benjamini_hochberg_p_values(p_values, benjamini_hochberg_column)
    path_to_p_values = Path(f'../results/{prefix}_p_values.csv')
    p_values.to_csv(str(path_to_p_values), index=False)


def get_parser(description: str):
    parser = argparse.ArgumentParser(description)
    parser.add_argument('graph-1', type=argparse.FileType, help='Path to first graph.')
    parser.add_argument('graph-2', type=argparse.FileType, help='Path to second graph.')
    parser.add_argument('-p', type=str, help='Prefix of result file. If not specified, a random prefix is generated.')
    parser.add_argument('-n', type=int, default=1000, help='Number of permutations. Default: 1000.')
    return parser