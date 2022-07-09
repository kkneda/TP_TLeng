from networkx import DiGraph, find_cycle
from networkx.exception import NetworkXNoCycle
from itertools import chain

def tipos_no_primitivos_de_una_lista_de_declaraciones(lista_de_declaraciones):
    # armo una lista de las listas de no primitivos de las declaraciones
    listas_de_listas_de_no_primitivos = map( 
        lambda x: x.tipos_no_primitivos(),
        lista_de_declaraciones,
    )
    
    # uno la lista de listas en una sola, devolviendo el conjunto de no primitivos que derivan de las declaraciones
    lista_de_no_primitivos = set(chain(*listas_de_listas_de_no_primitivos))
    
    return lista_de_no_primitivos

def buscar_dependencias_circulares(dicc):
		# Se arma el grafo de dependencias
    grafo_de_dependencias = DiGraph()
    for nombre, declaraciones in dicc.items():
        grafo_de_dependencias.add_node(nombre)
        vecinos = tipos_no_primitivos_de_una_lista_de_declaraciones(declaraciones)
        aristas = zip([nombre]*len(vecinos), vecinos)
        grafo_de_dependencias.add_edges_from(aristas)
    
    try:
        ciclo = find_cycle(grafo_de_dependencias, orientation="original")
        return ciclo # Si no se genera excepcion, hay ciclo y se lo retorna.
    except NetworkXNoCycle:
        return None # Si se genera excepcion, no hay ciclos.


def buscar_dependencias_no_declaradas(dicc):
    for clase, declaraciones in dicc.items():
        dependencias_no_primitivas = tipos_no_primitivos_de_una_lista_de_declaraciones(declaraciones)
        for dependencia_no_primitiva in dependencias_no_primitivas:
            if dependencia_no_primitiva not in dicc:
            		# Una dependencia no primitiva que no este en dicc es una dependencia no declarada:
                return dependencia_no_primitiva
    # Si toda dependencia no primitiva esta en dicc, no hay dependencias no declaradas:
    return None