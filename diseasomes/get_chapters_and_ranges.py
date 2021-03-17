import pandas as pd


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


def get_code_to_group_mapping(codes, group_type):
    groups = pd.read_csv(f'../data/icd10_{group_type}.tsv', sep='\t')
    codes_to_groups = {}
    for code in codes:
        if code == 'global':
            codes_to_groups[code] = 'Global'
        elif group_type == 'chapters':
            codes_to_groups[code] = _find_chapter(groups, code)
        else:
            codes_to_groups[code] = _find_range(groups, code)
    return codes_to_groups
