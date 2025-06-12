from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
import json

# Importar las clases de rutas desde el módulo de dominio
from domain.route import RutaInfo, NodoAVLRuta


class AVLRutas: 
    def __init__(self):
        self.root: Optional[NodoAVLRuta] = None
        self._total_rutas = 0
        self._total_usos = 0
    
    # ==================== MÉTODOS DE UTILIDAD AVL ====================
    
    def _altura(self, nodo: Optional[NodoAVLRuta]) -> int:
        """Obtiene la altura de un nodo"""
        return -1 if nodo is None else nodo.height
    
    def _balance(self, nodo: Optional[NodoAVLRuta]) -> int:
        """Calcula el factor de balance de un nodo"""
        return 0 if nodo is None else self._altura(nodo.left) - self._altura(nodo.right)
    
    def _actualizar_altura(self, nodo: NodoAVLRuta) -> None:
        """Actualiza la altura de un nodo"""
        nodo.height = max(self._altura(nodo.left), self._altura(nodo.right)) + 1
    
    def _rotar_derecha(self, y: NodoAVLRuta) -> NodoAVLRuta:
        """Rotación a la derecha"""
        x = y.left
        T2 = x.right
        
        # Realizar rotación
        x.right = y
        y.left = T2
        
        # Actualizar alturas
        self._actualizar_altura(y)
        self._actualizar_altura(x)
        
        return x
    
    def _rotar_izquierda(self, x: NodoAVLRuta) -> NodoAVLRuta:
        """Rotación a la izquierda"""
        y = x.right
        T2 = y.left
        
        # Realizar rotación
        y.left = x
        x.right = T2
        
        # Actualizar alturas
        self._actualizar_altura(x)
        self._actualizar_altura(y)
        
        return y
    
    # ==================== OPERACIONES PRINCIPALES ====================
    
    def insertar_ruta(self, ruta_info: RutaInfo) -> None:
        self.root = self._insertar_recursivo(self.root, ruta_info)
    
    def _insertar_recursivo(self, nodo: Optional[NodoAVLRuta], ruta_info: RutaInfo) -> NodoAVLRuta:
        """Inserción recursiva con balanceo automático"""
        # Inserción normal de BST
        if nodo is None:
            self._total_rutas += 1
            self._total_usos += ruta_info.frecuencia_uso
            return NodoAVLRuta(ruta_info)
        
        if ruta_info.ruta_id < nodo.key:
            nodo.left = self._insertar_recursivo(nodo.left, ruta_info)
        elif ruta_info.ruta_id > nodo.key:
            nodo.right = self._insertar_recursivo(nodo.right, ruta_info)
        else:
            # Ruta ya existe, actualizar información
            frecuencia_anterior = nodo.ruta_info.frecuencia_uso
            nodo.ruta_info = ruta_info
            self._total_usos += (ruta_info.frecuencia_uso - frecuencia_anterior)
            return nodo
        
        # Actualizar altura
        self._actualizar_altura(nodo)
        
        # Obtener factor de balance
        balance = self._balance(nodo)
        
        # Casos de rotación
        # Izquierda-Izquierda
        if balance > 1 and ruta_info.ruta_id < nodo.left.key:
            return self._rotar_derecha(nodo)
        
        # Derecha-Derecha
        if balance < -1 and ruta_info.ruta_id > nodo.right.key:
            return self._rotar_izquierda(nodo)
        
        # Izquierda-Derecha
        if balance > 1 and ruta_info.ruta_id > nodo.left.key:
            nodo.left = self._rotar_izquierda(nodo.left)
            return self._rotar_derecha(nodo)
        
        # Derecha-Izquierda
        if balance < -1 and ruta_info.ruta_id < nodo.right.key:
            nodo.right = self._rotar_derecha(nodo.right)
            return self._rotar_izquierda(nodo)
        
        return nodo
    
    def buscar_ruta(self, ruta_id: str) -> Optional[RutaInfo]:
        """Busca una ruta por su ID"""
        nodo = self._buscar_recursivo(self.root, ruta_id)
        return nodo.ruta_info if nodo else None
    
    def _buscar_recursivo(self, nodo: Optional[NodoAVLRuta], ruta_id: str) -> Optional[NodoAVLRuta]:
        """Búsqueda recursiva en el AVL"""
        if nodo is None or nodo.key == ruta_id:
            return nodo
        
        if ruta_id < nodo.key:
            return self._buscar_recursivo(nodo.left, ruta_id)
        else:
            return self._buscar_recursivo(nodo.right, ruta_id)
    
    def incrementar_uso_ruta(self, ruta_id: str, incremento: int = 1) -> bool:
       
        nodo = self._buscar_recursivo(self.root, ruta_id)
        if nodo:
            nodo.ruta_info.frecuencia_uso += incremento
            nodo.ruta_info.ultimo_uso = datetime.now()
            self._total_usos += incremento
            return True
        return False
    
    def eliminar_ruta(self, ruta_id: str) -> bool:
       
        tamaño_inicial = self._total_rutas
        self.root = self._eliminar_recursivo(self.root, ruta_id)
        return self._total_rutas < tamaño_inicial
    
    def _eliminar_recursivo(self, nodo: Optional[NodoAVLRuta], ruta_id: str) -> Optional[NodoAVLRuta]:
        """Eliminación recursiva con balanceo"""
        if nodo is None:
            return nodo
        
        if ruta_id < nodo.key:
            nodo.left = self._eliminar_recursivo(nodo.left, ruta_id)
        elif ruta_id > nodo.key:
            nodo.right = self._eliminar_recursivo(nodo.right, ruta_id)
        else:
            # Nodo a eliminar encontrado
            self._total_rutas -= 1
            self._total_usos -= nodo.ruta_info.frecuencia_uso
            
            if nodo.left is None or nodo.right is None:
                nodo = nodo.left or nodo.right
            else:
                # Nodo con dos hijos
                temp = self._nodo_minimo(nodo.right)
                nodo.key = temp.key
                nodo.ruta_info = temp.ruta_info
                nodo.right = self._eliminar_recursivo(nodo.right, temp.key)
        
        if nodo is None:
            return nodo
        
        # Actualizar altura y rebalancear
        self._actualizar_altura(nodo)
        balance = self._balance(nodo)
        
        # Rotaciones para rebalancear
        if balance > 1 and self._balance(nodo.left) >= 0:
            return self._rotar_derecha(nodo)
        
        if balance > 1 and self._balance(nodo.left) < 0:
            nodo.left = self._rotar_izquierda(nodo.left)
            return self._rotar_derecha(nodo)
        
        if balance < -1 and self._balance(nodo.right) <= 0:
            return self._rotar_izquierda(nodo)
        
        if balance < -1 and self._balance(nodo.right) > 0:
            nodo.right = self._rotar_derecha(nodo.right)
            return self._rotar_izquierda(nodo)
        
        return nodo
    
    def _nodo_minimo(self, nodo: NodoAVLRuta) -> NodoAVLRuta:
        current = nodo
        while current.left:
            current = current.left
        return current
    
    # ==================== CONSULTAS Y ANÁLISIS ====================
    
    def obtener_rutas_por_frecuencia(self, limite: Optional[int] = None, 
                                   orden_desc: bool = True) -> List[RutaInfo]:
        rutas = []
        self._recolectar_rutas_inorden(self.root, rutas)
        
        # Ordenar por frecuencia
        rutas.sort(key=lambda r: r.frecuencia_uso, reverse=orden_desc)
        
        return rutas[:limite] if limite else rutas
    
    def buscar_rutas_por_origen_destino(self, origen: str, destino: str) -> List[RutaInfo]:
 
        rutas = []
        self._buscar_por_origen_destino(self.root, origen, destino, rutas)
        return rutas
    
    def _buscar_por_origen_destino(self, nodo: Optional[NodoAVLRuta], 
                                 origen: str, destino: str, resultados: List[RutaInfo]) -> None:
       
        if nodo is None:
            return
        
        if (nodo.ruta_info.origen == origen and nodo.ruta_info.destino == destino):
            resultados.append(nodo.ruta_info)
        
        self._buscar_por_origen_destino(nodo.left, origen, destino, resultados)
        self._buscar_por_origen_destino(nodo.right, origen, destino, resultados)
    
    def obtener_estadisticas_uso(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas de uso de rutas"""
        if self._total_rutas == 0:
            return {
                'total_rutas': 0,
                'total_usos': 0,
                'uso_promedio': 0.0,
                'ruta_mas_usada': None,
                'ruta_menos_usada': None,
                'rutas_nunca_usadas': 0
            }
        
        rutas = self.obtener_rutas_por_frecuencia()
        rutas_nunca_usadas = len([r for r in rutas if r.frecuencia_uso == 0])
        
        return {
            'total_rutas': self._total_rutas,
            'total_usos': self._total_usos,
            'uso_promedio': self._total_usos / self._total_rutas,
            'ruta_mas_usada': rutas[0] if rutas else None,
            'ruta_menos_usada': rutas[-1] if rutas else None,
            'rutas_nunca_usadas': rutas_nunca_usadas,
            'altura_arbol': self._altura(self.root) + 1 if self.root else 0
        }
    
    def _recolectar_rutas_inorden(self, nodo: Optional[NodoAVLRuta], resultados: List[RutaInfo]) -> None:
        """Recolecta todas las rutas en orden"""
        if nodo is None:
            return
        
        self._recolectar_rutas_inorden(nodo.left, resultados)
        resultados.append(nodo.ruta_info)
        self._recolectar_rutas_inorden(nodo.right, resultados)
    
    def listar_todas_rutas(self) -> List[RutaInfo]:
        """Retorna lista de todas las rutas almacenadas"""
        rutas = []
        self._recolectar_rutas_inorden(self.root, rutas)
        return rutas
    
    # ==================== UTILIDADES ====================
    
    def esta_vacio(self) -> bool:
        return self.root is None
    
    def tamaño(self) -> int:
        return self._total_rutas
    
    def altura(self) -> int:
        return self._altura(self.root) + 1 if self.root else 0
    
    def es_balanceado(self) -> bool:
        return self._verificar_balance(self.root)
    
    def _verificar_balance(self, nodo: Optional[NodoAVLRuta]) -> bool:
        if nodo is None:
            return True
        
        balance = self._balance(nodo)
        if abs(balance) > 1:
            return False
        
        return (self._verificar_balance(nodo.left) and 
                self._verificar_balance(nodo.right))
    
    def imprimir_arbol(self) -> None:
        if self.root is None:
            print("Árbol vacío")
            return
        
        print("Estructura del AVL de Rutas:")
        self._imprimir_recursivo(self.root, "", True)
    
    def _imprimir_recursivo(self, nodo: Optional[NodoAVLRuta], prefijo: str, es_ultimo: bool) -> None:
        if nodo is not None:
            print(f"{prefijo}{'└── ' if es_ultimo else '├── '}{nodo}")
            extension = "    " if es_ultimo else "│   "
            
            if nodo.left is not None or nodo.right is not None:
                if nodo.right is not None:
                    self._imprimir_recursivo(nodo.right, prefijo + extension, nodo.left is None)
                if nodo.left is not None:
                    self._imprimir_recursivo(nodo.left, prefijo + extension, True)
      # ==================== SERIALIZACIÓN ====================
    
    def exportar_a_json(self, archivo: str) -> None:
        rutas = self.listar_todas_rutas()
        
    
        stats = self.obtener_estadisticas_uso()
        stats_serializables = stats.copy()
        
        if stats_serializables['ruta_mas_usada']:
            stats_serializables['ruta_mas_usada'] = stats_serializables['ruta_mas_usada'].to_dict()
        if stats_serializables['ruta_menos_usada']:
            stats_serializables['ruta_menos_usada'] = stats_serializables['ruta_menos_usada'].to_dict()
        
        datos = {
            'rutas': [ruta.to_dict() for ruta in rutas],
            'estadisticas': stats_serializables,
            'exportado_en': datetime.now().isoformat()
        }
        
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
    
    def importar_desde_json(self, archivo: str) -> int:
        with open(archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        rutas_importadas = 0
        for ruta_dict in datos.get('rutas', []):
            try:
                ruta_info = RutaInfo.from_dict(ruta_dict)
                self.insertar_ruta(ruta_info)
                rutas_importadas += 1
            except Exception as e:                print(f"Error importando ruta {ruta_dict.get('ruta_id', 'desconocida')}: {e}")
        
        return rutas_importadas
