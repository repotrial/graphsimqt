import pandas as pd


def _in_code_range(code_range, code):
    start, end = code_range.split('-')
    return start <= code <= end


def _find_chapter(chapters, code):
    for row in range(chapters.shape[0]):
        if _in_code_range(chapters.loc[row, 'Code Range'], code):
            return chapters.loc[row, 'Chapter'], chapters.loc[row, 'Description']
    raise RuntimeError(f'Did not find chapter for code {code}')


def _find_range(ranges, code):
    for row in range(ranges.shape[0]):
        if _in_code_range(ranges.loc[row, 'Code Range'], code):
            return ranges.loc[row, 'Range'], ranges.loc[row, 'Description']


def add_chapters_and_ranges(filename):
    data = pd.read_csv(filename)
    chapters = pd.read_csv('../data/icd_chapters.tsv', sep='\t')
    ranges = pd.read_csv('../data/icd_ranges.tsv', sep='\t')
    ranges['Range'] = [f'Range {i+1}' for i in range(ranges.shape[0])]
    chapter_col = []
    range_col = []
    for row in range(data.shape[0]):
        code = data.loc[row, 'comparison']
        if code == 'global':
            chapter_col.append('Global')
            range_col.append('Global')
        else:
            chapter, description = _find_chapter(chapters, code)
            chapter_col.append(chapter)
            icd_range, description = _find_range(ranges, code)
            range_col.append(icd_range)
    data['chapter'] = chapter_col
    data['range'] = range_col
    data.to_csv(filename, index=False)


if __name__ == '__main__':
    add_chapters_and_ranges('../results/empirical_p_values.csv')
    add_chapters_and_ranges('../results/permutation_results.csv')
