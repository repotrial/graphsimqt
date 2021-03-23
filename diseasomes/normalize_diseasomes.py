import graph_tool as gt
from pathlib import Path
from typing import List


def _compute_normalized_edge_property(graph: gt.Graph, property_name: str):
    prop = graph.edge_properties[property_name]
    max_val = max([prop[edge] for edge in graph.edges()])
    normalized_property = graph.new_ep('double')
    for edge in graph.edges():
        normalized_property[edge] = prop[edge] / max_val
    graph.edge_properties['NORM-SCORE'] = normalized_property


def _compute_normalized_edge_ranks(graph: gt.Graph, property_name: str):
    sorted_edges = []
    prop = graph.edge_properties[property_name]
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


def normalize_diseasomes(paths_to_graphs: List[Path], property_names: List[str]):

    for path_to_graph, property_name in zip(paths_to_graphs, property_names):
        graph = gt.load_graph(str(path_to_graph))
        _compute_normalized_edge_property(graph, property_name)
        _compute_normalized_edge_ranks(graph, property_name)
        path_to_normalized_graph = path_to_graph.parent.joinpath(f'normalized_{path_to_graph.name}')
        graph.save(str(path_to_normalized_graph))


if __name__ == '__main__':
    indices = ['relative_risk', 'jaccard_index', 'phi_correralation']
    normalize_diseasomes([Path(f'../data/{prefix}_diseasome.graphml') for prefix in indices], ['RR', 'JI', 'PC'])
