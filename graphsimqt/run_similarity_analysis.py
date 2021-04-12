from pathlib import Path
from typing import Union, List, Optional
from graphsimqt.normalize_graph import normalize_graph
from graphsimqt.run_permutation_tests import run_permutation_tests
from graphsimqt.compute_empirical_p_values import compute_empirical_p_values
from graphsimqt.compute_mwu_p_values import compute_mwu_p_values
from graphsimqt.utils.get_parsers import get_similarity_parser


def run_similarity_analysis(path_to_graph_1: Union[str, Path], path_to_graph_2: Union[str, Path],
                            result_directory_name: str, node_id_attribute_name: Optional[str] = None,
                            edge_score_attribute_name: Optional[str] = None, is_directed: Optional[bool] = None,
                            has_header: bool = False, normalization_method: Optional[str] = 'max',
                            num_permutations: int = 1000, adjust_method: str = 'holm-sidak',
                            paths_to_node_sets: List[Union[str, Path]] = [], silent: bool = False):
    """Runs the entire similarity analysis pipeline.

    Calls graphsimqt.normalize_graph.normalize_graph() on the input graphs and then sequentially runs
    graphsimqt.run_permutation_tests.run_permutation_tests(),
    graphsimqt.compute_empirical_p_values.compute_empirical_p_values(), and
    graphsimqt.compute_mwu_p_values.compute_mwu_p_values().

    Parameters
    ----------
    path_to_graph_1 : str or pathlib.Path
        Path to first graph. The File format is derived from the suffix. If the suffix is graphml,
        the  input is expected to be in GraphML format.
        Otherwise, an edge list with lines of the form <SOURCE><SEP><TARGET>[<SEP><SCORE>] is expected.
        The separator is derived from the suffix. csv: comma. csv2: semicolon. tsv: tab. wsv: whitespace.
        Providing edge scores is optional.
    path_to_graph_2 : str or pathlib.Path
        Path to second graph. The File format is derived from the suffix. If the suffix is graphml,
        the  input is expected to be in GraphML format.
        Otherwise, an edge list with lines of the form <SOURCE><SEP><TARGET>[<SEP><SCORE>] is expected.
        The separator is derived from the suffix. csv: comma. csv2: semicolon. tsv: tab. wsv: whitespace.
        Providing edge scores is optional.
    result_directory_name : str
        Name of the subdirectory of the results/ directory where the results should be saved.
        Will be created if it does not exist already.
    node_id_attribute_name : str, optional
        Name of node ID attribute to be used for GraphML input.
        If not provided, unique node attribute is used if available.
        Not used for edge list input.
    edge_score_attribute_name : str, optional
        Name of edge score attribute to be used for GraphML input.
        If not provided, unique edge attribute is used if available.
        Not used for edge list input.
    is_directed : bool, optional
        Specifies if graphs given as edge lists should be interpreted as directed (True) or undirected (False).
        Not used for GraphML input.
    has_header : bool, default: False
        Specifies if edge list input contains a header that should be skipped.
        Not used for GraphML input.
    normalization_method: {'max', 'max-min', 'z-score'}, default: 'max'
        Method used to normalize the scores.
        'max': divide all scores by maximum. 'max-min': Max-min normalization. 'z-score': Z-score normalization.
    num_permutations : int, default: 1000
        Number of permutations.
    adjust_method : str, default: 'holm-sidak'
        Method used for adjusting the p-values.
        Can be set to any of the methods available in statsmodels.stats.multitest.multipletests().
    paths_to_node_sets : list of str or pathlib.Path, default: []
        List of paths to node sets files in either JSON or tabular format for which MWU p-values should be computed.
        JSON files are expected to contain named lists of node IDs.
        Tabular files are expected to contain one column named 'node' with the node IDs
        and one or several columns for categorical variables, i.e., partitions of the node IDs.
        For tabular data, the separator is derived from the suffix.
        csv: comma. csv2: semicolon. tsv: tab. 'wsv: whitespace.
    silent : bool, default: False
        Set to True to suppress printing progress to stdout.

    """
    graph_1 = normalize_graph(path_to_graph_1, node_id_attribute_name, edge_score_attribute_name, is_directed,
                              has_header, normalization_method, silent, False)
    graph_2 = normalize_graph(path_to_graph_2, node_id_attribute_name, edge_score_attribute_name, is_directed,
                              has_header, normalization_method, silent, False)
    run_permutation_tests(graph_1, graph_2, result_directory_name, num_permutations, silent)
    compute_empirical_p_values(result_directory_name, adjust_method, silent)
    compute_mwu_p_values(result_directory_name, adjust_method, paths_to_node_sets, silent)


if __name__ == '__main__':
    args = get_similarity_parser('run_similarity_analysis').parse_args()
    run_similarity_analysis(args.path_to_graph_1, args.path_to_graph_2, args.dirname, args.id, args.score,
                            args.directed, args.header, args.normalization, args.permutations, args.adjust,
                            args.nodesets, args.silent)
