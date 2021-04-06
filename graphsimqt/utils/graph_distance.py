import graph_tool as gt
import numpy as np
from typing import List, Dict


class GraphDistance(object):

    def __init__(self, g: gt.Graph, h: gt.Graph, node_ids, edge_properties=None):
        self.global_distance = None
        self.local_distances = {node_id: None for node_id in node_ids}
        self._compute_distances(g, h, edge_properties)

    def as_dict(self):
        return {'global_distance': self.global_distance, 'local_distances': self.local_distances}

    def __repr__(self):
        return str(self.as_dict())

    @staticmethod
    def _map_ids_to_nodes(graph: gt.Graph):
        node_id_property = graph.vertex_properties['ID']
        return {node_id_property[node]: node for node in graph.vertices()}

    def _compute_local_distance(self, g: gt.Graph, h: gt.Graph, node_id: str, g_ids_to_nodes: Dict[str, gt.Vertex],
                                h_ids_to_nodes: Dict[str, gt.Vertex], edge_properties: List[gt.EdgePropertyMap],
                                kind: str):
        g_node_ids = g.vertex_properties['ID']
        h_node_ids = h.vertex_properties['ID']
        node_g = g_ids_to_nodes[node_id]
        node_h = h_ids_to_nodes[node_id]
        if kind == 'all':
            neighbors_g = {g_node_ids[node] for node in g.get_all_neighbors(node_g)}
            neighbors_h = {h_node_ids[node] for node in h.get_all_neighbors(node_h)}
        elif kind == 'in':
            neighbors_g = {g_node_ids[node] for node in g.get_in_neighbors(node_g)}
            neighbors_h = {h_node_ids[node] for node in h.get_in_neighbors(node_h)}
        elif kind == 'out':
            neighbors_g = {g_node_ids[node] for node in g.get_out_neighbors(node_g)}
            neighbors_h = {h_node_ids[node] for node in h.get_out_neighbors(node_h)}
        neighbors_only_g = neighbors_g.difference(neighbors_h)
        neighbors_only_h = neighbors_h.difference(neighbors_g)
        if not edge_properties:
            self.local_distances[node_id] += float(len(neighbors_only_g) + len(neighbors_only_h))
        else:
            neighbors_both = neighbors_g.intersection(neighbors_h)
            for node_id_nb in neighbors_both:
                if kind == 'in':
                    edge_g = g.edge(g_ids_to_nodes[node_id_nb], node_g)
                    edge_h = h.edge(h_ids_to_nodes[node_id_nb], node_h)
                else:
                    edge_g = g.edge(node_g, g_ids_to_nodes[node_id_nb])
                    edge_h = h.edge(node_h, h_ids_to_nodes[node_id_nb])
                self.local_distances[node_id] += np.fabs(edge_properties[0][edge_g] - edge_properties[1][edge_h])
            for node_id_nb in neighbors_only_g:
                if kind == 'in':
                    edge_g = g.edge(g_ids_to_nodes[node_id_nb], node_g)
                else:
                    edge_g = g.edge(node_g, g_ids_to_nodes[node_id_nb])
                self.local_distances[node_id] += 1.0 + edge_properties[0][edge_g]
            for node_id_nb in neighbors_only_h:
                if kind == 'in':
                    edge_h = h.edge(h_ids_to_nodes[node_id_nb], node_h)
                else:
                    edge_h = h.edge(node_h, h_ids_to_nodes[node_id_nb])
                self.local_distances[node_id] += 1.0 + edge_properties[1][edge_h]

    def _compute_distances(self, g: gt.Graph, h: gt.Graph, edge_properties: List[gt.EdgePropertyMap]):
        g_ids_to_nodes = self._map_ids_to_nodes(g)
        h_ids_to_nodes = self._map_ids_to_nodes(h)
        self.global_distance = 0.0
        for node_id in self.local_distances:
            self.local_distances[node_id] = 0.0
            if g.is_directed():
                self._compute_local_distance(g, h, node_id, g_ids_to_nodes, h_ids_to_nodes, edge_properties, 'in')
                self._compute_local_distance(g, h, node_id, g_ids_to_nodes, h_ids_to_nodes, edge_properties, 'out')
            else:
                self._compute_local_distance(g, h, node_id, g_ids_to_nodes, h_ids_to_nodes, edge_properties, 'all')
            self.global_distance += (self.local_distances[node_id] / 2)