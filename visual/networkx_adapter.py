import networkx as nx

class NetworkXAdapter:
    """Adaptador para integración con NetworkX"""
    
    def __init__(self, graph):
        self.graph = graph
    
    def to_networkx(self):
        """Convierte el grafo interno a NetworkX"""
        G = nx.Graph()
        
        # Agregar nodos
        for node_id, node in self.graph.nodes.items():
            G.add_node(node_id, 
                      type=node.type.name,
                      name=node.name,
                      x=node.x,
                      y=node.y)
        
        # Agregar aristas
        for node_id, neighbors in self.graph.edges.items():
            for neighbor_id, weight in neighbors:
                if not G.has_edge(node_id, neighbor_id):
                    G.add_edge(node_id, neighbor_id, weight=weight)
        
        return G