import numpy as np
import graph_tool as gt
import pandas as pd
import json
import itertools as itt


def construct_diseasome():

    # Read data.
    jaccard_indices = pd.DataFrame(data=np.load('data/no_hierarchy_icd10_diseaseome_jaccard.npz')['arr_0'])
    with open('data/no_hierarchy_icd10_diseaseome_cols.json') as fp:
        diseases = json.load(fp)

    # Create graph and add nodes.
    ji_graph = gt.Graph(directed=False)
    disease_to_node = {disease: ji_graph.add_vertex() for disease in diseases}
    icd_10_codes = ji_graph.new_vp('string', vals=diseases)
    ji_graph.vertex_properties['ICD-10'] = icd_10_codes

    # Add edges with Jaccard indices.
    edge_list = []
    for source, target in itt.combinations(range(ji_graph.num_vertices()), 2):
        if jaccard_indices.loc[source, target] > 0:
            edge_list.append((source, target, jaccard_indices.loc[source, target]))
    jaccard_index = ji_graph.new_ep('double')
    ji_graph.add_edge_list(edge_list, eprops=[jaccard_index])
    ji_graph.edge_properties['JI'] = jaccard_index
    ji_graph.num_edges()

    # Save diseasome.
    ji_graph.save('../data/jaccard_index_diseasome.graphml')


if __name__ == '__main__':
    construct_diseasome()
