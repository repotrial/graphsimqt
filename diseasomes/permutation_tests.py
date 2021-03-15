import graph_tool as gt
import graph_tool.generation as gtg
import pandas as pd
from diseasomes.graph_distance import GraphDistance


def add_line_to_results(results, permuted, comparison, distance, distance_type):
    results['permuted'].append(permuted)
    results['comparison'].append(comparison)
    results['distance'].append(distance)
    results['distance_type'].append(distance_type)


def run_permutation_tests(num_permutations=1000):
    rr_graph = gt.load_graph('../data/normalized_relative_risk_diseasome.graphml')
    ji_graph = gt.load_graph('../data/normalized_jaccard_index_diseasome.graphml')
    icd_10_codes = [rr_graph.vertex_properties['ICD-10'][node] for node in rr_graph.vertices()]
    results = {'permuted': [], 'comparison': [], 'distance': [], 'distance_type': []}
    props = {'topology_only': None,
             'normalized_scores': (rr_graph.edge_properties['RR-NORM'], ji_graph.edge_properties['JI-NORM']),
             'normalized_ranks': (rr_graph.edge_properties['RR-NORM-RANK'], ji_graph.edge_properties['JI-NORM-RANK'])}

    for distance_type, prop in props.items():
        dist = GraphDistance(rr_graph, ji_graph, icd_10_codes, prop)
        add_line_to_results(results, False, 'global', dist.global_distance, distance_type)
        for icd_10_code, distance in dist.local_distances.items():
            add_line_to_results(results, False, icd_10_code, distance, distance_type)

    for _ in range(num_permutations):
        gtg.random_rewire(rr_graph, n_iter=100)
        gtg.random_rewire(ji_graph, n_iter=100)
        for distance_type, prop in props.items():
            dist = GraphDistance(rr_graph, ji_graph, icd_10_codes, prop)
            add_line_to_results(results, True, 'global', dist.global_distance, distance_type)
            for icd_10_code, distance in dist.local_distances.items():
                add_line_to_results(results, True, icd_10_code, distance, distance_type)

    results = pd.DataFrame(data=results)
    results.to_csv('../results/permutation_results.csv', index=False)


if __name__ == '__main__':
    run_permutation_tests(1000)
