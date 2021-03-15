import graph_tool as gt
import graph_tool.generation as gtg
import numpy as np


class GraphDistance(object):

    def __init__(self, g: gt.Graph, h: gt.Graph, icd_10_codes, edge_properties=None):
        self.global_distance = None
        self.local_distances = {icd_10_code: None for icd_10_code in icd_10_codes}
        g_icd_10_to_nodes = self._map_icd_10_codes_to_nodes(g)
        h_icd_10_to_nodes = self._map_icd_10_codes_to_nodes(h)
        self._compute_global_distance(g, h, g_icd_10_to_nodes, h_icd_10_to_nodes, edge_properties)
        self._compute_local_distances(g, h, g_icd_10_to_nodes, h_icd_10_to_nodes, edge_properties)

    def as_dict(self):
        return {'global_distance': self.global_distance, 'local_distances': self.local_distances}

    def __str__(self):
        return str(self.as_dict())

    @staticmethod
    def _map_icd_10_codes_to_nodes(graph: gt.Graph):
        icd_10_prop = graph.vertex_properties['ICD-10']
        return {icd_10_prop[node]: node for node in graph.vertices()}

    @staticmethod
    def _get_edge(graph: gt.Graph, source, target, icd_10_to_nodes):
        return graph.edge(icd_10_to_nodes[source], icd_10_to_nodes[target])

    def _compute_global_distance(self, g, h, g_icd_10_to_nodes, h_icd_10_to_nodes, edge_props):
        icd_10_g = g.vertex_properties['ICD-10']
        icd_10_h = h.vertex_properties['ICD-10']
        edges_only_g = []
        edges_both = []
        edges_only_h = []
        for edge_g in g.edges():
            edge_h = self._get_edge(h, icd_10_g[edge_g.source()], icd_10_g[edge_g.target()], h_icd_10_to_nodes)
            if edge_h:
                edges_both.append((edge_g, edge_h))
            else:
                edges_only_g.append(edge_g)
        for edge_h in h.edges():
            if not self._get_edge(g, icd_10_h[edge_h.source()], icd_10_h[edge_h.target()], g_icd_10_to_nodes):
                edges_only_h.append(edge_h)
        if not edge_props:
            self.global_distance = float(len(edges_only_g) + len(edges_only_h))
        else:
            self.global_distance = 0.0
            for edge_g in edges_only_g:
                self.global_distance += 1.0 + edge_props[0][edge_g]
            for edge_h in edges_only_h:
                self.global_distance += 1.0 + edge_props[1][edge_h]
            for edge_g, edge_h in edges_both:
                self.global_distance += np.fabs(edge_props[0][edge_g] - edge_props[1][edge_h])

    def _compute_local_distances(self, g, h, g_icd_10_to_nodes, h_icd_10_to_nodes, edge_props):
        icd_10_g = g.vertex_properties['ICD-10']
        icd_10_h = h.vertex_properties['ICD-10']
        for icd_10_code in self.local_distances:
            node_g = g_icd_10_to_nodes[icd_10_code]
            node_h = h_icd_10_to_nodes[icd_10_code]
            neighbors_g = {icd_10_g[node] for node in g.get_all_neighbors(node_g)}
            neighbors_h = {icd_10_h[node] for node in h.get_all_neighbors(node_h)}
            neighbors_only_g = neighbors_g.difference(neighbors_h)
            neighbors_only_h = neighbors_h.difference(neighbors_g)
            if not edge_props:
                self.local_distances[icd_10_code] = float(len(neighbors_only_g) + len(neighbors_only_h))
            else:
                self.local_distances[icd_10_code] = 0.0
                neighbors_both = neighbors_g.intersection(neighbors_h)
                for icd_10_code_nb in neighbors_both:
                    edge_g = g.edge(node_g, g_icd_10_to_nodes[icd_10_code_nb])
                    edge_h = h.edge(node_h, h_icd_10_to_nodes[icd_10_code_nb])
                    self.local_distances[icd_10_code] += np.fabs(edge_props[0][edge_g] - edge_props[1][edge_h])
                for icd_10_code_nb in neighbors_only_g:
                    edge_g = g.edge(node_g, g_icd_10_to_nodes[icd_10_code_nb])
                    self.local_distances[icd_10_code] += 1.0 + edge_props[0][edge_g]
                for icd_10_code_nb in neighbors_only_h:
                    edge_h = h.edge(node_h, h_icd_10_to_nodes[icd_10_code_nb])
                    self.local_distances[icd_10_code] += 1.0 + edge_props[1][edge_h]


if __name__ == '__main__':
    g = gt.load_graph('../data/normalized_relative_risk_diseasome.graphml')
    h = gt.load_graph('../data/normalized_jaccard_index_diseasome.graphml')
    #gtg.random_rewire(h, n_iter=100)
    icd_10_codes = [g.vertex_properties['ICD-10'][node] for node in g.vertices()]
    edge_props = (g.edge_properties['RR-NORM-RANK'], h.edge_properties['JI-NORM-RANK'])
    dist = GraphDistance(g, h, icd_10_codes, edge_props)
    print(f'global_distance = {dist.global_distance}\n'
          f'sum_local_distances / 2 = {sum([d for _, d in dist.local_distances.items()])/ 2}')
    gtg.random_rewire(g, n_iter=100)
    gtg.random_rewire(h, n_iter=100)
    #edge_props = (g.edge_properties['RR-NORM-RANK'], h.edge_properties['JI-NORM-RANK'])
    dist = GraphDistance(g, h, icd_10_codes, edge_props)
    print(f'global_distance = {dist.global_distance}\n'
          f'sum_local_distances / 2 = {sum([d for _, d in dist.local_distances.items()]) / 2}')
    print(dist)