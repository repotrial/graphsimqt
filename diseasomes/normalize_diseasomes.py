import graph_tool as gt


def _compute_normalized_edge_property(graph: gt.Graph, property_name: str):
    prop = graph.edge_properties[property_name]
    max_val = max([prop[edge] for edge in graph.edges()])
    normalized_property = graph.new_ep('double')
    for edge in graph.edges():
        normalized_property[edge] = prop[edge] / max_val
    graph.edge_properties[f'{property_name}-NORM'] = normalized_property


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
    graph.edge_properties[f'{property_name}-NORM-RANK'] = normalized_rank


def normalize_diseasomes():

    # Load diseasomes.
    rr_graph = gt.load_graph('data/relative_risk_diseasome.graphml')
    ji_graph = gt.load_graph('data/jaccard_index_diseasome.graphml')

    # Collect nodes contained in both diseasomes.
    rr_diseases = {rr_graph.vertex_properties['ICD-10'][node] for node in rr_graph.vertices()}
    ji_diseases = {ji_graph.vertex_properties['ICD-10'][node] for node in ji_graph.vertices()}
    common_diseases = rr_diseases.intersection(ji_diseases)
    rr_is_common_node = rr_graph.new_vp('bool')
    for node in rr_graph.vertices():
        rr_is_common_node[node] = rr_graph.vertex_properties['ICD-10'][node] in common_diseases
    ji_is_common_node = ji_graph.new_vp('bool')
    for node in ji_graph.vertices():
        ji_is_common_node[node] = ji_graph.vertex_properties['ICD-10'][node] in common_diseases

    # Delete all nodes that are not contained in one of the two diseasomes.
    rr_graph.set_vertex_filter(rr_is_common_node)
    rr_graph.purge_vertices()
    rr_graph.clear_filters()
    ji_graph.set_vertex_filter(ji_is_common_node)
    ji_graph.purge_vertices()
    ji_graph.clear_filters()

    # Compute normalized scores and edge ranks.
    _compute_normalized_edge_property(rr_graph, 'RR')
    _compute_normalized_edge_ranks(rr_graph, 'RR')
    _compute_normalized_edge_property(ji_graph, 'JI')
    _compute_normalized_edge_ranks(ji_graph, 'JI')

    # Save normalized diseasomes.
    ji_graph.save('../data/normalized_jaccard_index_diseasome.graphml')
    rr_graph.save('../data/normalized_relative_risk_diseasome.graphml')


if __name__ == '__main__':
    normalize_diseasomes()