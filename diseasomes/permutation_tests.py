import graph_tool as gt
import graph_tool.generation as gtg
import pandas as pd
from pathlib import Path
import uuid
from diseasomes.graph_distance import GraphDistance
from diseasomes.utils import get_code_to_group_mapping, get_parser


def _add_line_to_results(results: dict, permuted: bool, comparison: str, distance: float, distance_type: str,
                         icd_range: str, icd_chapter: str):
    results['permuted'].append(permuted)
    results['comparison'].append(comparison)
    results['distance'].append(distance)
    results['distance_type'].append(distance_type)
    results['range'].append(icd_range)
    results['chapter'].append(icd_chapter)


def _discard_non_common_diseases(graph_1: gt.Graph, graph_2: gt.Graph):
    diseases_1 = {graph_1.vertex_properties['ICD-10'][node] for node in graph_1.vertices()}
    diseases_2 = {graph_2.vertex_properties['ICD-10'][node] for node in graph_2.vertices()}
    common_diseases = diseases_1.intersection(diseases_2)
    is_common_node_1 = graph_1.new_vp('bool')
    for node in graph_1.vertices():
        is_common_node_1[node] = graph_1.vertex_properties['ICD-10'][node] in common_diseases
    is_common_node_2 = graph_2.new_vp('bool')
    for node in graph_2.vertices():
        is_common_node_2[node] = graph_2.vertex_properties['ICD-10'][node] in common_diseases
    graph_1.set_vertex_filter(is_common_node_1)
    graph_1.purge_vertices()
    graph_1.clear_filters()
    graph_2.set_vertex_filter(is_common_node_2)
    graph_2.purge_vertices()
    graph_2.clear_filters()


def run_permutation_tests(path_graph_1: Path, path_graph_2: Path, result_file_prefix: str = None,
                          num_permutations: int = 1000):
    graph_1 = gt.load_graph(str(path_graph_1))
    graph_2 = gt.load_graph(str(path_graph_2))
    _discard_non_common_diseases(graph_1, graph_2)
    icd_10_codes = [graph_1.vertex_properties['ICD-10'][node] for node in graph_1.vertices()]
    code_to_range = get_code_to_group_mapping(icd_10_codes, 'ranges')
    code_to_chapter = get_code_to_group_mapping(icd_10_codes, 'chapters')
    results = {'permuted': [], 'comparison': [], 'distance': [], 'distance_type': [], 'chapter': [], 'range': []}
    props = {'topology_only': None,
             'normalized_scores': (graph_1.edge_properties['NORM-SCORE'], graph_2.edge_properties['NORM-SCORE']),
             'normalized_ranks': (graph_1.edge_properties['NORM-RANK'], graph_2.edge_properties['NORM-RANK'])}

    for distance_type, prop in props.items():
        dist = GraphDistance(graph_1, graph_2, icd_10_codes, prop)
        _add_line_to_results(results, False, 'global', dist.global_distance, distance_type, 'Global', 'Global')
        for icd_10_code, distance in dist.local_distances.items():
            icd_range = code_to_range[icd_10_code]
            icd_chapter = code_to_chapter[icd_10_code]
            _add_line_to_results(results, False, icd_10_code, distance, distance_type, icd_range, icd_chapter)

    for _ in range(num_permutations):
        gtg.random_rewire(graph_1, n_iter=100)
        gtg.random_rewire(graph_2, n_iter=100)
        for distance_type, prop in props.items():
            dist = GraphDistance(graph_1, graph_2, icd_10_codes, prop)
            _add_line_to_results(results, True, 'global', dist.global_distance, distance_type, 'Global', 'Global')
            for icd_10_code, distance in dist.local_distances.items():
                icd_range = code_to_range[icd_10_code]
                icd_chapter = code_to_chapter[icd_10_code]
                _add_line_to_results(results, True, icd_10_code, distance, distance_type, icd_range, icd_chapter)

    results = pd.DataFrame(data=results)
    if not result_file_prefix:
        result_file_prefix = uuid.uuid4()
    results.to_csv(f'../results/{result_file_prefix}_permutation_results.csv', index=False)


if __name__ == '__main__':
    args = get_parser('Run permutation tests.').parse_args()
    run_permutation_tests(args.graph_1, args.graph_2, args.p, args.n)
