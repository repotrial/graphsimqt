import graph_tool as gt
from typing import Union, Tuple, Optional
from pathlib import Path
from graphsimqt.compute_shortest_path_distances import compute_shortest_path_distances
from graphsimqt.analyze_shortest_path_distances import analyze_shortest_path_distances
from graphsimqt.utils.get_parsers import get_shortest_path_parser


def run_shortest_path_analysis(reference_graph: Union[str, Path, gt.Graph], distance_graph: Union[str, Path, gt.Graph],
                               result_directory_name: str, reference_node_id_attribute_name: Optional[str] = None,
                               distance_node_id_attribute_name: Optional[str] = None,
                               reference_edge_score_attribute_name: Optional[str] = None,
                               exclude_terminals: bool = True,
                               exclude_as_connectors: Optional[Tuple[str, str]] = None, silent: bool = False):
    """Runs the entire shortest path analysis pipeline.

    Sequentially runs graphsimqt.compute_shortest_path_distances.compute_shortest_path_distances() and
    graphsimqt.analyze_shortest_path_distances.analyze_shortest_path_distances().

    Parameters
    ----------
    reference_graph : str or pathlib.Path or graph_tool.Graph
        Path to reference graph. Distances are computed for all pairs of nodes contained in this graph.
    distance_graph : srr or pathlib.Path or graph_tool.Graph
        Path to graph in which the distances should be computed.
    result_directory_name : str
        Name of the subdirectory of the results/ directory where the results should be saved.
        Will be created if it does not exist already.
    reference_node_id_attribute_name : str, optional
        Name of node ID attribute in reference graph.
        If not provided, unique node attribute is used if available.
    distance_node_id_attribute_name : str, optional
        Name of node ID attribute in distance graph.
        If not provided, unique node attribute is used if available.
    reference_edge_score_attribute_name : str, optional
        Name of edge score attribute in reference graph.
        If not provided, unique node attribute is used if available.
    exclude_terminals : bool, default: True
        Specifies whether to exclude terminals as inner nodes in shortest paths.
    exclude_as_connectors : tuple of (str, str), optional
        Key-value pair, where the key is a node attribute name in the distance graph.
        All nodes with the specified value are excluded as inner nodes in the shortest paths.
    silent : bool
        Set to True to suppress printing progress to stdout.

    """
    compute_shortest_path_distances(reference_graph, distance_graph, result_directory_name,
                                    reference_node_id_attribute_name, distance_node_id_attribute_name,
                                    reference_edge_score_attribute_name, exclude_terminals, exclude_as_connectors,
                                    silent)
    analyze_shortest_path_distances(result_directory_name, silent)


if __name__ == '__main__':
    args = get_shortest_path_parser('run_shortest_path_analysis').parse_args()
    run_shortest_path_analysis(args.path_to_reference_graph, args.path_to_distance_graph, args.dirname,
                               args.reference_id, args.distance_id, args.score, not args.use_terminals,
                               args.exclude_as_connectors, args.silent)
