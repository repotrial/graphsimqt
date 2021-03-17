import graph_tool as gt
import numpy as np


class GraphDistance(object):

    def __init__(self, g: gt.Graph, h: gt.Graph, icd_10_codes, edge_properties=None):
        self.global_distance = None
        self.local_distances = {icd_10_code: None for icd_10_code in icd_10_codes}
        g_icd_10_to_nodes = self._map_icd_10_codes_to_nodes(g)
        h_icd_10_to_nodes = self._map_icd_10_codes_to_nodes(h)
        self._compute_distances(g, h, g_icd_10_to_nodes, h_icd_10_to_nodes, edge_properties)

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

    def _compute_distances(self, g, h, g_icd_10_to_nodes, h_icd_10_to_nodes, edge_properties):
        icd_10_g = g.vertex_properties['ICD-10']
        icd_10_h = h.vertex_properties['ICD-10']
        self.global_distance = 0.0
        for icd_10_code in self.local_distances:
            node_g = g_icd_10_to_nodes[icd_10_code]
            node_h = h_icd_10_to_nodes[icd_10_code]
            neighbors_g = {icd_10_g[node] for node in g.get_all_neighbors(node_g)}
            neighbors_h = {icd_10_h[node] for node in h.get_all_neighbors(node_h)}
            neighbors_only_g = neighbors_g.difference(neighbors_h)
            neighbors_only_h = neighbors_h.difference(neighbors_g)
            if not edge_properties:
                self.local_distances[icd_10_code] = float(len(neighbors_only_g) + len(neighbors_only_h))
            else:
                self.local_distances[icd_10_code] = 0.0
                neighbors_both = neighbors_g.intersection(neighbors_h)
                for icd_10_code_nb in neighbors_both:
                    edge_g = g.edge(node_g, g_icd_10_to_nodes[icd_10_code_nb])
                    edge_h = h.edge(node_h, h_icd_10_to_nodes[icd_10_code_nb])
                    self.local_distances[icd_10_code] += np.fabs(edge_properties[0][edge_g] - edge_properties[1][edge_h])
                for icd_10_code_nb in neighbors_only_g:
                    edge_g = g.edge(node_g, g_icd_10_to_nodes[icd_10_code_nb])
                    self.local_distances[icd_10_code] += 1.0 + edge_properties[0][edge_g]
                for icd_10_code_nb in neighbors_only_h:
                    edge_h = h.edge(node_h, h_icd_10_to_nodes[icd_10_code_nb])
                    self.local_distances[icd_10_code] += 1.0 + edge_properties[1][edge_h]
            self.global_distance += (self.local_distances[icd_10_code] / 2)
