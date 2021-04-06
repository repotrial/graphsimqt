import graph_tool as gt
import pandas as pd
from pathlib import Path
from typing import Optional, Union
import warnings
import argparse
from progress.spinner import Spinner


def _compute_normalized_edge_scores(graph: gt.Graph, normalization_method: Optional[str]):
    scores = graph.edge_properties['SCORE'].a
    supported_methods = {'max', 'max-min', 'z-score'}
    if normalization_method not in supported_methods:
        warnings.warn(f'Unsupported normalization method {normalization_method}, using max instead.\n'
                      f'Supported normalization methods: {", ".join(supported_methods)}.')
        normalization_method = 'max'
    if normalization_method == 'max':
        normalized_scores = scores / scores.max()
    elif normalization_method == 'max-min':
        normalized_scores = (scores - scores.min()) / (scores.max() - scores.min())
    else:
        normalized_scores = (scores - scores.mean()) / scores.std()
    normalized_property = graph.new_ep('double', vals=normalized_scores)
    graph.edge_properties['NORM-SCORE'] = normalized_property


def _compute_normalized_edge_ranks(graph: gt.Graph):
    sorted_edges = []
    prop = graph.edge_properties['SCORE']
    for edge in graph.edges():
        sorted_edges.append((edge, prop[edge]))
    sorted_edges.sort(key=lambda item: item[1])
    normalized_rank = graph.new_ep('double')
    num_lower = -1
    last_val = 0
    for edge, val in sorted_edges:
        if val > last_val:
            num_lower += 1
        normalized_rank[edge] = (num_lower + 1.0) / graph.num_edges()
    graph.edge_properties['NORM-RANK'] = normalized_rank


def _load_edge_list(path_to_graph: Path, is_directed: Optional[bool], has_header: bool) -> gt.Graph:
    if not isinstance(is_directed, bool):
        raise ValueError(f'If the graph is given as an edge list, the directedness must be specified via the '
                         f'parameter is_directed.')
    sep = {'.csv': ',', '.wsv': ' ', '.tsv': '\t', '.csv2': ';'}[path_to_graph.suffix]
    if has_header:
        edge_list = pd.read_csv(str(path_to_graph), sep=sep)
    else:
        edge_list = pd.read_csv(str(path_to_graph), sep=sep, header=None)
    columns = edge_list.columns
    has_score = len(columns) > 2
    if has_score:
        edge_list.rename(columns={columns[0]: 'source', columns[1]: 'target', columns[2]: 'score'}, inplace=True)
    else:
        edge_list.rename(columns={columns[0]: 'source', columns[1]: 'target'}, inplace=True)
    node_ids = list(set(edge_list['source']).union(edge_list['target']))
    graph = gt.Graph(directed=is_directed)
    node_id_to_node = {node_id: graph.add_vertex() for node_id in node_ids}
    node_id_property = graph.new_vp('string', vals=node_ids)
    graph.vertex_properties['ID'] = node_id_property
    edges = []
    for i in range(edge_list.shape[0]):
        source = node_id_to_node[edge_list.loc[i, 'source']]
        target = node_id_to_node[edge_list.loc[i, 'target']]
        if has_score:
            edges.append((source, target, float(edge_list.loc[i, 'score'])))
        else:
            edges.append((source, target))
    if has_score:
        edge_score_property = graph.new_ep('double')
        graph.add_edge_list(edges, eprops=[edge_score_property])
        graph.edge_properties['SCORE'] = edge_score_property
    else:
        graph.add_edge_list(edges)
    return graph


def _ensure_node_id_property(graph: gt.Graph, path_to_graph: Path, node_id_attribute_name: Optional[str]):
    if node_id_attribute_name and not node_id_attribute_name in graph.vertex_properties:
        raise ValueError(f'The network {str(path_to_graph)} does not contain a node attribute with '
                         f'name {node_id_attribute_name}.')
    node_attribute_names = list(graph.vertex_properties.keys())
    if not node_id_attribute_name:
        if len(node_attribute_names) > 1:
            raise ValueError(f'The network {str(path_to_graph)} has more than 1 node attribute.\n'
                             f'Please specify node ID attribute via the parameter node_id_attribute_name.')
        elif len(node_attribute_names) == 0:
            raise ValueError(f'The network {str(path_to_graph)} has more than 0 node attributes.\n'
                             f'A node ID attribute is required for .graphml networks.')
        else:
            node_id_attribute_name = node_attribute_names[0]
    if node_id_attribute_name != 'ID':
        node_id_property = graph.vertex_properties[node_id_attribute_name].copy()
        node_id_attribute_name = 'ID'
        graph.vertex_properties[node_id_attribute_name] = node_id_property
    for node_attribute_name in node_attribute_names:
        if node_attribute_name != node_id_property:
            del graph.vertex_properties[node_attribute_name]
    node_id_property = graph.vertex_properties[node_id_attribute_name]
    if node_id_property.python_value_type() is not str:
        node_id_property = node_id_property.copy(value_type='string')
        del graph.vertex_properties[node_id_attribute_name]
        graph.vertex_properties[node_id_attribute_name] = node_id_property
    if len(set(node_id_property)) < graph.num_vertices():
        raise ValueError('Invalid node ID attribute. Cannot contain duplicates.')


def _ensure_edge_score_property(graph: gt.Graph, path_to_graph: Path, edge_score_attribute_name: Optional[str]):
    if edge_score_attribute_name and not edge_score_attribute_name in graph.edge_properties:
        raise ValueError(f'The network {str(path_to_graph)} does not contain an edge attribute with '
                         f'name {edge_score_attribute_name}.')
    edge_attribute_names = list(graph.edge_properties.keys())
    if len(edge_attribute_names) > 0:
        if not edge_score_attribute_name:
            if len(edge_attribute_names) > 1:
                raise ValueError(f'The network {str(path_to_graph)} has more than 1 edge attribute.\n'
                                 f'Please specify edge score attribute via the parameter edge_score_attribute_name.')
            else:
                edge_score_attribute_name = edge_attribute_names[0]
        if edge_score_attribute_name != 'SCORE':
            edge_score_property = graph.edge_properties[edge_score_attribute_name].copy()
            edge_score_attribute_name = 'SCORE'
            graph.edge_properties[edge_score_attribute_name] = edge_score_property
        for edge_attribute_name in edge_attribute_names:
            if edge_attribute_name != edge_score_attribute_name:
                del graph.edge_properties[edge_attribute_name]
        edge_score_property = graph.edge_properties[edge_score_attribute_name]
        if edge_score_property.python_value_type() is int:
            edge_score_property = edge_score_property.copy(value_type='double')
            del graph.edge_properties[edge_score_attribute_name]
            graph.edge_properties[edge_score_attribute_name] = edge_score_property
        if edge_score_property.python_value_type() is not float:
            raise ValueError(f'Invalid edge score data type {edge_score_property.value_type()}. '
                             f'Must be float or int.')


def _load_graphml(path_to_graph: Path, node_id_attribute_name: Optional[str],
                  edge_score_attribute_name: Optional[str], is_directed: Optional[bool]) -> gt.Graph:
    graph = gt.load_graph(str(path_to_graph))
    _ensure_node_id_property(graph, path_to_graph, node_id_attribute_name)
    _ensure_edge_score_property(graph, path_to_graph, edge_score_attribute_name)
    if isinstance(is_directed, bool) and (graph.is_directed() != is_directed):
        warnings.warn(f'The value for parameter is_directed ({is_directed}) contradicts the specification '
                      f'provided in {str(path_to_graph)} ({graph.is_directed()}).\n'
                      f'Using .graphml specification ({graph.is_directed()}).')
    return graph


def normalize_graph(path_to_graph: Union[str, Path], node_id_attribute_name: Optional[str] = None,
                    edge_score_attribute_name: Optional[str] = None, is_directed: Optional[bool] = None,
                    has_header: bool = False, normalization_method: Optional[str] = 'max', silent: bool = False):
    """Generates normalized version input graph to be used for similarity quantification and saves it as GraphML file.

    Parameters
    ----------
    path_to_graph : str or pathlib.Path
        Path to graph that should be normalized. The File format is derived from the suffix. If the suffix is graphml,
        the  input is expected to be in GraphML format.
        Otherwise, an edge list with lines of the form <SOURCE><SEP><TARGET>[<SEP><SCORE>] is expected.
        The separator is derived from the suffix. csv: comma. csv2: semicolon. tsv: tab. wsv: whitespace.
        Providing edge scores is optional.
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
    silent : bool, default: False
        Set to True to suppress printing progress to stdout.

    """
    if not silent:
        spinner = Spinner(f'Normalizing graph {str(path_to_graph)}. ')
        spinner.next()
    if isinstance(path_to_graph, str):
        path_to_graph = Path(path_to_graph)
    supported_formats = {'.graphml', '.csv', '.csv2', '.tsv', '.wsv'}
    if path_to_graph.suffix == '.graphml':
        graph = _load_graphml(path_to_graph, node_id_attribute_name, edge_score_attribute_name, is_directed)
    elif path_to_graph.suffix in supported_formats:
        graph = _load_edge_list(path_to_graph, is_directed, has_header)
    else:
        raise ValueError(f'Unsupported file format {path_to_graph.suffix}.\n'
                         f'Supported formats: {", ".join(supported_formats)}.')
    if not silent:
        spinner.next()
    if len(graph.edge_properties) > 0:
        _compute_normalized_edge_scores(graph, normalization_method)
        if not silent:
            spinner.next()
        _compute_normalized_edge_ranks(graph)
        if not silent:
            spinner.next()
    path_to_normalized_graph = path_to_graph.parent.joinpath(f'normalized_{path_to_graph.stem}.graphml')
    graph.save(str(path_to_normalized_graph))
    if not silent:
        spinner.finish()
        print(f'Saved normalized graph to {str(path_to_normalized_graph)}.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Normalize input network.')
    parser.add_argument('graph', type=Path, help='Path to graph that should be normalized. The file format is derived '
                                                 'from the suffix. If the suffix is graphml, the  input is expected to '
                                                 'be in GraphML format. Otherwise, an edge list with lines of the form '
                                                 '<SOURCE><SEP><TARGET>[<SEP><SCORE>] is expected. The separator is '
                                                 'derived from the suffix. csv: comma. csv2: semicolon. tsv: tab. wsv: '
                                                 'whitespace. Providing edge scores is optional.')
    parser.add_argument('--id', type=str, help='Name of node ID attribute to be used for GraphML input. If not '
                                               'provided, unique node attribute is used if available. Not used for '
                                               'edge list input.')
    parser.add_argument('--score', type=str, help='Name of edge score attribute to be used for GraphML input. If not '
                                                  'provided, unique edge attribute is used if available. Not used for'
                                                  'edge list input.')
    parser.add_argument('--directed', type=bool, help='Specifies if graphs given as edge lists should be interpreted '
                                                      'as directed (True) or undirected (False). Not used for GraphML '
                                                      'input.')
    parser.add_argument('--header', action='store_true', help='Set this flag if your input is given as an edge list '
                                                              'with a header that should be skipped. Not used for '
                                                              'GraphML input.')
    parser.add_argument('--normalization', type=str, help='Method used to normalize the scores. max: divide all scores '
                                                          'by maximum. max-min: Max-min normalization. z-score: '
                                                          'Z-score normalization. Default: max.', default='max',
                        choices=['max', 'max-min', 'z-score'])
    parser.add_argument('--silent', action='store_true', help='Set this flag to suppress printing progress to stdout.')
    args = parser.parse_args()
    normalize_graph(args.graph, args.id, args.score, args.directed, args.header, args.normalization, args.silent)
