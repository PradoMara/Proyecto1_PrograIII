class AVLNode:
    """Nodo del árbol AVL para almacenar rutas y su frecuencia"""
    
    def __init__(self, route_key, frequency=1):
        self.route_key = route_key  # String que representa la ruta (ej: "A->B->C")
        self.frequency = frequency  # Frecuencia de uso de esta ruta
        self.left = None
        self.right = None
        self.height = 1
    
    def __str__(self):
        return f"{self.route_key}\nFreq: {self.frequency}"


class AVLTree:
    """Árbol AVL para registrar y analizar frecuencia de rutas"""
    
    def __init__(self):
        self.root = None
    
    def get_height(self, node):
        """Obtiene la altura de un nodo"""
        if not node:
            return 0
        return node.height
    
    def get_balance(self, node):
        """Obtiene el factor de balance de un nodo"""
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)
    
    def rotate_right(self, y):
        """Rotación hacia la derecha"""
        x = y.left
        T2 = x.right
        
        # Realizar rotación
        x.right = y
        y.left = T2
        
        # Actualizar alturas
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        
        return x
    
    def rotate_left(self, x):
        """Rotación hacia la izquierda"""
        y = x.right
        T2 = y.left
        
        # Realizar rotación
        y.left = x
        x.right = T2
        
        # Actualizar alturas
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        
        return y
    
    def insert(self, root, route_key):
        """Inserta una ruta en el AVL o incrementa su frecuencia"""
        # Paso 1: Inserción BST normal
        if not root:
            return AVLNode(route_key)
        
        if route_key < root.route_key:
            root.left = self.insert(root.left, route_key)
        elif route_key > root.route_key:
            root.right = self.insert(root.right, route_key)
        else:
            # Ruta ya existe, incrementar frecuencia
            root.frequency += 1
            return root
        
        # Paso 2: Actualizar altura del nodo ancestro
        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))
        
        # Paso 3: Obtener factor de balance
        balance = self.get_balance(root)
        
        # Paso 4: Realizar rotaciones si es necesario
        # Caso Left Left
        if balance > 1 and route_key < root.left.route_key:
            return self.rotate_right(root)
        
        # Caso Right Right
        if balance < -1 and route_key > root.right.route_key:
            return self.rotate_left(root)
        
        # Caso Left Right
        if balance > 1 and route_key > root.left.route_key:
            root.left = self.rotate_left(root.left)
            return self.rotate_right(root)
        
        # Caso Right Left
        if balance < -1 and route_key < root.right.route_key:
            root.right = self.rotate_right(root.right)
            return self.rotate_left(root)
        
        return root
    
    def add_route(self, route_path):
        """Agrega una ruta al árbol AVL"""
        # Convertir los IDs de nodos a strings antes de hacer join
        if isinstance(route_path, list):
            route_key = " → ".join([str(node_id) for node_id in route_path])
        else:
            route_key = str(route_path)
        self.root = self.insert(self.root, route_key)
    
    def inorder_traversal(self, root, result):
        """Recorrido inorder para obtener rutas ordenadas"""
        if root:
            self.inorder_traversal(root.left, result)
            result.append((root.route_key, root.frequency))
            self.inorder_traversal(root.right, result)
    
    def get_all_routes(self):
        """Obtiene todas las rutas ordenadas por frecuencia descendente"""
        result = []
        self.inorder_traversal(self.root, result)
        # Ordenar por frecuencia descendente
        return sorted(result, key=lambda x: x[1], reverse=True)
    
    def get_most_frequent_routes(self, n=10):
        """Obtiene las n rutas más frecuentes"""
        all_routes = self.get_all_routes()
        return all_routes[:n]
    
    def get_tree_structure(self):
        """Obtiene la estructura del árbol para visualización"""
        if not self.root:
            return [], []
        
        nodes = []
        edges = []
        
        def traverse(node, node_id=0, parent_id=None):
            if not node:
                return node_id
            
            nodes.append((node_id, f"{node.route_key}\nFreq: {node.frequency}"))
            
            if parent_id is not None:
                edges.append((parent_id, node_id))
            
            current_id = node_id
            next_id = node_id + 1
            
            if node.left:
                next_id = traverse(node.left, next_id, current_id)
            
            if node.right:
                next_id = traverse(node.right, next_id, current_id)
            
            return next_id
        
        traverse(self.root)
        return nodes, edges
