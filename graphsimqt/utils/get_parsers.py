import argparse
from pathlib import Path


def get_shortest_path_parser(script_name: str) -> argparse.ArgumentParser:
    descriptions = {'compute_shortest_path_distances': 'Compute shortest path distances.',
                    'analyze_shortest_path_distances': 'Analyze shortest path distances.',
                    'run_shortest_path_analysis': 'Run shortest path analysis.'}
    parser = argparse.ArgumentParser(descriptions[script_name])
    if script_name in {'compute_shortest_path_distances', 'run_shortest_path_analysis'}:
        parser.add_argument('path_to_reference_graph', type=Path, help='Path to reference graph.')
        parser.add_argument('path_to_distance_graph', type=Path, help='Path to distance graph.')
        parser.add_argument('--dirname', type=str, help='Name of the subdirectory of the results/ directory where the '
                                                        'results should be saved. Will be created if it does not exist '
                                                        'already.', required=True)
        parser.add_argument('--reference_id', type=str, help='Name of node ID attribute in reference graph. If not '
                                                             'provided, unique node attribute is used if available.')
        parser.add_argument('--distance_id', type=str, help='Name of node ID attribute in distance graph. If not '
                                                            'provided, unique node attribute is used if available.')
        parser.add_argument('--score', type=str, help='Name of edge score attribute in reference graph. '
                                                      'If not provided, unique edge attribute is used if available.')
        parser.add_argument('--use_terminals', action='store_true', help='Use also terminals as connectors.')
        parser.add_argument('--exclude_as_connectors', type=str, nargs=2, help='Key-value pair of node attribute.')
        # parser.add_argument('--exclude_as_connectors', type=str, nargs=4, help='Key-value pair of node attribute.')
    else:
        parser.add_argument('--dirname', type=str, help='Name of the subdirectory of the results/ directory where the '
                                                        'results generated by compute_shortest_path_distances.py can '
                                                        'be found.', required=True)
    parser.add_argument('--silent', action='store_true', help='Set this flag to suppress printing progress to stdout.')
    return parser


def get_similarity_parser(script_name: str) -> argparse.ArgumentParser:
    descriptions = {'compute_empirical_p_values': 'Compute empirical p-values.',
                    'compute_mwu_p_values': 'Compute MWU p-values.',
                    'normalize_graph': 'Normalize input graph.',
                    'run_permutation_tests': 'Run permutation tests.',
                    'run_similarity_analysis': 'Run similarity analysis.'}
    parser = argparse.ArgumentParser(descriptions[script_name])

    # Add paths to graph(s) and .
    graph_file_format_help = 'The file format is derived from the suffix. If the suffix is graphml or gt, the  input ' \
                             'is expected to be in GraphML format (binarized if suffix is gt). Otherwise, an edge ' \
                             'list with lines of the form <SOURCE><SEP><TARGET>[<SEP><SCORE>] is expected. The ' \
                             'separator is derived from the suffix. csv: comma. csv2: semicolon. tsv: tab. wsv: ' \
                             'whitespace. Providing edge scores is optional.'
    if script_name == 'normalize_graph':
        parser.add_argument('graph', type=Path, help=f'Path to graph. {graph_file_format_help}')
    elif script_name == 'run_permutation_tests':
        parser.add_argument('path_to_graph_1', type=Path, help='Path to first normalized input graph generated by '
                                                               'normalize_graph.py.')
        parser.add_argument('path_to_graph_2', type=Path, help='Path to second normalized input graph generated by '
                                                               'normalize_graph.py.')
    elif script_name == 'run_similarity_analysis':
        parser.add_argument('path_to_graph_1', type=Path, help=f'Path to first graph. {graph_file_format_help}')
        parser.add_argument('path_to_graph_2', type=Path, help=f'Path to second graph. {graph_file_format_help}')

    # Add parameters for graph normalization.
    if script_name in {'normalize_graph', 'run_similarity_analysis'}:
        parser.add_argument('--id', type=str, help='Name of node ID attribute to be used for GraphML input. If not '
                                                   'provided, unique node attribute is used if available. Not used for '
                                                   'edge list input.')
        parser.add_argument('--score', type=str, help='Name of edge score attribute to be used for GraphML input. '
                                                      'If not provided, unique edge attribute is used if available. '
                                                      'Not used for edge list input.')
        parser.add_argument('--directed', type=bool, help='Specifies if graphs given as edge lists should be '
                                                          'interpreted as directed (True) or undirected (False). Not '
                                                          'used for GraphML input.')
        parser.add_argument('--header', action='store_true', help='Set this flag if your input is given as an edge '
                                                                  'list with a header that should be skipped. Not used '
                                                                  'for GraphML input.')
        parser.add_argument('--normalization', type=str, help='Method used to normalize the scores. max: divide all '
                                                              'scores by maximum. max-min: Max-min normalization. '
                                                              'z-score: Z-score normalization. Default: max.',
                            default='max', choices=['max', 'max-min', 'z-score'])

    # Add argument for result directory.
    if script_name in {'run_permutation_tests', 'run_similarity_analysis'}:
        parser.add_argument('--dirname', type=str, help='Name of the subdirectory of the results/ directory where the '
                                                        'results should be saved. Will be created if it does not exist '
                                                        'already.', required=True)
    elif script_name in {'compute_empirical_p_values', 'compute_mwu_p_values'}:
        parser.add_argument('--dirname', type=str, help='Name of the subdirectory of the results/ directory where the '
                                                        'results generated by run_permutation_tests.py can be found '
                                                        'and the p-values should be saved.', required=True)

    # Add argument for adjust method.
    if script_name in {'compute_empirical_p_values', 'compute_mwu_p_values', 'run_similarity_analysis'}:
        parser.add_argument('--adjust', type=str, help='Method used for adjusting p-values. Can be set to any of the '
                                                       'methods in statsmodels.stats.multitest.multipletests().',
                            default='holm-sidak')

    # Add argument for node sets.
    if script_name in {'compute_mwu_p_values', 'run_similarity_analysis'}:
        parser.add_argument('--nodesets', type=Path, help='Paths to node set files in either JSON or tabular format '
                                                          'for which MWU p-values should be computed. JSON files are '
                                                          'expected to contain named lists of node IDs. Tabular files '
                                                          'are expected to contain one column named "node" with the '
                                                          'node IDs and one or several columns for categorical '
                                                          'variables, i.e., partitions of the node IDs. For tabular '
                                                          'data, the separator is derived from the suffix. csv: comma. '
                                                          'csv2: semicolon. tsv: tab. wsv: whitespace.', nargs='+',
                            default=[])
    # Add silent flag.
    parser.add_argument('--silent', action='store_true', help='Set this flag to suppress printing progress to stdout.')
    return parser
