import graph_tool as gt
import pandas as pd
from pathlib import Path


def construct_diseasome():

    # Read data and collect ICD-10 codes.
    dtb = pd.read_csv(str(Path('../data/dtb.tsv')), sep='\t')
    diseases = list(set(dtb['D1']).union(set(dtb['D2'])))

    # Create graph and add nodes.
    rr_graph = gt.Graph(directed=False)
    disease_to_node = {disease: rr_graph.add_vertex() for disease in diseases}
    icd_10_codes = rr_graph.new_vp('string', vals=diseases)
    rr_graph.vertex_properties['ICD-10'] = icd_10_codes

    # Add edges with relative risks. Use mean relative risk if DTB data has edges in both directions.
    edges = {}
    for i in range(dtb.shape[0]):
        d1 = dtb.loc[i, 'D1']
        d2 = dtb.loc[i, 'D2']
        rr = dtb.loc[i, 'RR']
        if rr > 1:
            node_1 = disease_to_node[d1]
            node_2 = disease_to_node[d2]
            if (node_2, node_1) in edges:
                edges[(node_2, node_1)] += rr
                edges[(node_2, node_1)] /= 2
            else:
                edges[(node_1, node_2)] = rr
    relative_risk = rr_graph.new_ep('double')
    edge_list = [(edge[0], edge[1], rr) for edge, rr in edges.items()]
    rr_graph.add_edge_list(edge_list, eprops=[relative_risk])
    rr_graph.edge_properties['RR'] = relative_risk

    # Save diseasome.
    rr_graph.save(str(Path('../data/relative_risk_diseasome.graphml')))


if __name__ == '__main__':
    construct_diseasome()
