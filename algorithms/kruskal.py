# Algoritmo de Kruskal para encontrar el Árbol de Expansión Mínima (MST)

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Compresión de caminos
        return self.parent[x]
    
    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False  # Ya están en el mismo conjunto
        
        # Unión por rango
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
        
        return True


class KruskalMST:
    def __init__(self):
        self.edges = []
        self.vertices = set()
        self.mst_edges = []
        self.total_weight = 0
    
    def add_edge(self, u, v, weight):
        self.edges.append((weight, u, v))
        self.vertices.add(u)
        self.vertices.add(v)
    
    def find_mst(self):
        if not self.edges:
            return [], 0
        
        # Crear mapeo de vértices a índices
        vertex_list = sorted(list(self.vertices))
        vertex_to_index = {v: i for i, v in enumerate(vertex_list)}
        n_vertices = len(vertex_list)
        
        # Ordenar aristas por peso
        sorted_edges = sorted(self.edges)
        
        # Inicializar Union-Find
        uf = UnionFind(n_vertices)
        
        # Variables para el resultado
        mst_edges = []
        total_weight = 0
        
        # Procesar aristas en orden de peso
        for weight, u, v in sorted_edges:
            u_idx = vertex_to_index[u]
            v_idx = vertex_to_index[v]
            
            # Si los vértices no están conectados, agregar la arista al MST
            if uf.union(u_idx, v_idx):
                mst_edges.append((u, v, weight))
                total_weight += weight
                
                # Si tenemos n-1 aristas, el MST está completo
                if len(mst_edges) == n_vertices - 1:
                    break
        
        # Guardar resultados
        self.mst_edges = mst_edges
        self.total_weight = total_weight
        
        return mst_edges, total_weight
