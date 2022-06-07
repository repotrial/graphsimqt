import graph_tool as gt
import graph_tool.topology as gtt
from typing import Union, Tuple, Optional, List, Dict, Sequence
from pathlib import Path
import pandas as pd
import itertools as itt
import numpy as np
from progress.spinner import Spinner
from progress.bar import IncrementalBar
from graphsimqt.utils.get_directory_paths import get_result_directory_path
from graphsimqt.utils.get_parsers import get_shortest_path_parser


def _get_node_ids(graph: gt.Graph, node_id_attribute_name: Optional[str]) -> gt.VertexPropertyMap:
    if not node_id_attribute_name:
        if len(graph.vp) > 1:
            raise ValueError(f'One of the two input graphs has more than 1 node attribute.\n'
                             f'Please specify node ID attribute via the parameter node_id_attribute_name.')
        elif len(graph.vp) == 0:
            raise ValueError(f'One of the two input graphs has 0 node attributes.\n'
                             f'Node ID attributes are required to align the nodes.')
        else:
            node_id_attribute_name = list(graph.vp.keys())[0]
    return graph.vp[node_id_attribute_name]


def _get_attributes(reference_graph: gt.Graph, distance_graph: gt.Graph,
                    reference_node_id_attribute_name: Optional[str],
                    distance_node_id_attribute_name: Optional[str],
                    reference_edge_score_attribute_name: Optional[str]) -> Tuple[gt.VertexPropertyMap,
                                                                                 gt.VertexPropertyMap,
                                                                                 Optional[gt.EdgePropertyMap]]:
    ref_ids = _get_node_ids(reference_graph, reference_node_id_attribute_name)
    dist_ids = _get_node_ids(distance_graph, distance_node_id_attribute_name)
    if not reference_edge_score_attribute_name and len(reference_graph.ep) == 1:
        reference_edge_score_attribute_name = list(reference_graph.ep.keys())[0]
    ref_scores = None
    if reference_edge_score_attribute_name:
        ref_scores = reference_graph.ep[reference_edge_score_attribute_name]
    return ref_ids, dist_ids, ref_scores


def _initialize_node_filter(distance_graph: gt.Graph, exclude_as_connectors: Optional[Sequence[Tuple[str, str]]],
                            exclude_terminals: bool, ref_ids: gt.VertexPropertyMap,
                            dist_ids: gt.VertexPropertyMap) -> gt.VertexPropertyMap:
    node_filter = distance_graph.new_vp('boolean', val=False)
    if exclude_as_connectors:

        for node in distance_graph.vertices():
            node_filter[node] = (distance_graph.vp[exclude_as_connectors[0]][node] == exclude_as_connectors[1])
            # modify here to be able to filter for two dif. node types
            # for c in exclude_as_connectors:
            #     node_filter[node] = (distance_graph.vp[c[0]][node] == c[1])
    if exclude_terminals:
        ref_ids_as_set = set(ref_ids)
        for node in distance_graph.vertices():
            node_filter[node] = (node_filter[node] or (dist_ids[node] in ref_ids_as_set))
    distance_graph.set_vertex_filter(node_filter, inverted=True)
    return node_filter


def _get_terminals(distance_graph: gt.Graph, ref_ids: gt.VertexPropertyMap,
                   dist_ids: gt.VertexPropertyMap) -> List[gt.Vertex]:
    dist_ids_to_nodes = {dist_ids[node]: node for node in distance_graph.vertices()}
    terminals = [dist_ids_to_nodes[node_id] for node_id in set(ref_ids).intersection(set(dist_ids))]
    terminals = [node for node in terminals if distance_graph.get_total_degrees([node])[0] > 0]
    return terminals


def _compute_distance(reference_graph: gt.Graph, distance_graph: gt.Graph, dist_ids: gt.VertexPropertyMap,
                      ref_ids_to_nodes: Dict[str, gt.Vertex], node_filter: gt.VertexPropertyMap, source: gt.Vertex,
                      target: gt.Vertex, edge_scores: Optional[gt.EdgePropertyMap], distances: Dict[str, list]):
    filter_source = node_filter[source]
    filter_target = node_filter[target]
    node_filter[source] = node_filter[target] = False
    distance = gtt.shortest_distance(distance_graph, source, target, directed=False)
    if distance > distance_graph.num_vertices():
        distance = np.inf
    node_filter[source] = filter_source
    node_filter[target] = filter_target
    distances['source'].append(dist_ids[source])
    distances['target'].append(dist_ids[target])
    distances['distance'].append(distance)
    # if distance_graph.vp['TYPE'][source] == 'drug':
    #     edge = reference_graph.edge(ref_ids_to_nodes[dist_ids[source]], ref_ids_to_nodes[dist_ids[target]])
    # elif distance_graph.vp['TYPE'][source] == 'disease':
    #     edge = reference_graph.edge(ref_ids_to_nodes[dist_ids[target]], ref_ids_to_nodes[dist_ids[source]])
    edge = reference_graph.edge(ref_ids_to_nodes[dist_ids[source]], ref_ids_to_nodes[dist_ids[target]])
    distances['reference_edge'].append(bool(edge))
    if edge and edge_scores:
        distances['reference_score'].append(edge_scores[edge])
    else:
        distances['reference_score'].append(None)


def compute_shortest_path_distances(reference_graph: Union[str, Path, gt.Graph],
                                    distance_graph: Union[str, Path, gt.Graph],
                                    result_directory_name: str, reference_node_id_attribute_name: Optional[str] = None,
                                    distance_node_id_attribute_name: Optional[str] = None,
                                    reference_edge_score_attribute_name: Optional[str] = None,
                                    exclude_terminals: bool = True,
                                    exclude_as_connectors: Optional[Sequence[Tuple[str, str]]] = None, silent: bool = False):
    """Computes shortest path distances.

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
    if not silent:
        spinner = Spinner('Preparing computation of shortest path distances. ')
        spinner.next()
    if not isinstance(reference_graph, gt.Graph):
        reference_graph = gt.load_graph(str(reference_graph))
    if not isinstance(distance_graph, gt.Graph):
        distance_graph = gt.load_graph(str(distance_graph))
    if not silent:
        spinner.next()
    ref_ids, dist_ids, edge_scores = _get_attributes(reference_graph, distance_graph, reference_node_id_attribute_name,
                                                     distance_node_id_attribute_name,
                                                     reference_edge_score_attribute_name)
    if not silent:
        spinner.next()
    terminals = _get_terminals(distance_graph, ref_ids, dist_ids)
    if not silent:
        spinner.next()
    node_filter = _initialize_node_filter(distance_graph, exclude_as_connectors, exclude_terminals, ref_ids, dist_ids)
    distances = {'source': [], 'target': [], 'distance': [], 'reference_edge': [], 'reference_score': []}
    ref_ids_to_nodes = {ref_ids[node]: node for node in reference_graph.vertices()}
    if not silent:
        spinner.finish()
        bar = IncrementalBar('Computing shortest path distances.', max=len(terminals) * (len(terminals) - 1) / 2)
    for source, target in itt.combinations(terminals, 2):
        if not silent:
            bar.next()
        # For drug-disease distances uncomment the following if statement, since we don't want dr-dr or dis-dis distances when we're computing dr-dis distances
        # if distance_graph.vp['TYPE'][source] != distance_graph.vp['TYPE'][target]:
        #     _compute_distance(reference_graph, distance_graph, dist_ids, ref_ids_to_nodes, node_filter, source, target,
        #                   edge_scores, distances)
        _compute_distance(reference_graph, distance_graph, dist_ids, ref_ids_to_nodes, node_filter, source, target,
                          edge_scores, distances)
    if not silent:
        bar.finish()
        spinner = Spinner('Saving shortest path distances. ')
        spinner.next()
    distances = pd.DataFrame(data=distances)
    result_dir_path = get_result_directory_path(result_directory_name)
    result_dir_path.mkdir(exist_ok=True)
    path_to_distances = result_dir_path.joinpath('shortest_path_distances.csv')
    distances.to_csv(str(path_to_distances), index=False)
    if not silent:
        spinner.finish()
        print(f'Saved shortest path distances to {str(path_to_distances)}.')


if __name__ == '__main__':
    args = get_shortest_path_parser('compute_shortest_path_distances').parse_args()
    compute_shortest_path_distances(args.path_to_reference_graph, args.path_to_distance_graph, args.dirname,
                                    args.reference_id, args.distance_id, args.score, not args.use_terminals,
                                    args.exclude_as_connectors, args.silent)
