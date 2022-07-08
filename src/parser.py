from networkx import DiGraph, is_directed_acyclic_graph, find_cycle
from networkx.exception import NetworkXNoCycle
from itertools import chain
import sys
import random
import string
import ply.yacc as yacc

from lexer import tokens

# start -> tipo
# tipo -> TYPE ID STRUCT { lista } tipo | .
# lista -> ID arreglo BASIC_TYPE lista | ID arreglo ID lista | ID arreglo STRUCT { lista } lista | .
# arreglo -> [ ] arreglo | .

tabulacion = " " * 2

def ejemplificar_lista_declaraciones(lista_de_declaraciones, dicc_clases, cant_tabs):
    json = '{\n'
    for i, declaracion in enumerate(lista_de_declaraciones):
        json += declaracion.ejemplo(dicc_clases, cant_tabs + 1) + (",\n" if i < len(lista_de_declaraciones) - 1 else "\n")
    json += tabulacion * cant_tabs + '}'
    return json
    
def crear_ejemplo(dicc_clases, clase_principal):
		return ejemplificar_lista_declaraciones(dicc_clases[clase_principal], dicc_clases, 0)
    
def ejemplo_tipo_basico(tipo_basico):
    # devuelve el ejemplo del string output de un tipo basico
    if tipo_basico == 'int':
        return str(random.randint(0, 100))
    elif tipo_basico == 'bool':
        return str(True if random.random() >= 0.5 else False)
    elif tipo_basico == 'float64':
        return str(round(random.random() * 1000, 1))
    elif tipo_basico == 'string':
        caracteres = string.ascii_lowercase # es un string que contiene todos los caracteres del regex [a-z]
        random_string = ''.join(random.choice(caracteres) for i in range(random.randint(1, 10)))
        return '"' + random_string + '"'

def tipos_no_primitivos_de_una_lista_de_declaraciones(lista_de_declaraciones):
    # armo una lista de las listas de no primitivos de las declaraciones
    listas_de_listas_de_no_primitivos = map( 
        lambda x: x.tipos_no_primitivos(),
        lista_de_declaraciones,
    )
    
    # uno la lista de listas en una sola, devolviendo el conjunto de no primitivos que derivan de las declaraciones
    lista_de_no_primitivos = set(chain(*listas_de_listas_de_no_primitivos))
    
    return lista_de_no_primitivos
    
def ejemplo_array(tipo, dimension, dicc_clases, cant_tabs):
    if dimension == 0:
        res = tipo.ejemplo(dicc_clases, cant_tabs)
    else:
        posiciones = random.randint(0, 5)
        if posiciones == 0:
            res = "[]"
        else:
            res = "[ \n"
            for posicion in range(0, posiciones):
                res += (cant_tabs+1) * tabulacion + ejemplo_array(tipo, dimension - 1, dicc_clases, cant_tabs + 1) + (",\n" if posicion < posiciones - 1 else "\n")
            res += cant_tabs * tabulacion + "]"
    return res

class Declaracion:
    # las declaraciones son de la forma:
    # nombre_variable tipo_variable dimension
    # donde el nombre_variable es el indicador del atributo de la clase o estructura declarada,
    # tipo variable es el tipo correspondiente (basic type, struct o uno previamente declarado)
    # y la dimension indica la cantidad de arreglos anidados del atributo
    def __init__(self, nombre_var, tipo, dimension):
        self.nombre_var = nombre_var # nombre del atributo
        self.tipo = tipo # tipo del atributo
        self.dimension = dimension # dimension del atributo
        
    def tipos_no_primitivos(self):
        # devuelve una lista con los tipos no primitivos que descienden de esta declaracion
        return self.tipo.no_primitivos()
    
    def ejemplo(self, dicc_clases, cant_tabs):
        return tabulacion * cant_tabs + '"' + self.nombre_var + '"' + ":" + ejemplo_array(self.tipo, self.dimension, dicc_clases, cant_tabs)
    
    def __repr__(self):
        return str(self.nombre_var) + " " +  str(self.tipo) + " " + str(self.dimension)

class Tipo:
    def __init__(self, categoria, es_primitivo):
        self.categoria = categoria # que clase de tipo es (un tipo indicado  por un string o un struct)
        self.es_primitivo = es_primitivo # un Tipo es primitivo si su categoria pertenece a los basic types
        
    def no_primitivos(self):
        # devuelve una lista con los tipos no primitivos ligados a la categoria de este tipo
        
        # en el caso en el cual la categoria es una estructura,
        # devuelve la lista de los tipos no primidivos de sus declaraciones
        if isinstance(self.categoria, Estructura):
            return self.categoria.no_primitivos()
        
        # en el caso en el cual no es una estructura, ni un tipo primitivo,
        # devuelve la lista que contiene solo al valor de la categoria (el string del tipo o ID.val)
        elif not self.es_primitivo:
            return [self.categoria]
        
        # en el caso en el que es un tipo primitivo se devuelve la lista vacia
        else:
            return []
        
    def ejemplo(self, dicc_clases, cant_tabs):
        if isinstance(self.categoria, Estructura):
            return self.categoria.ejemplo(dicc_clases, cant_tabs)
        
        elif not self.es_primitivo:
            return ejemplificar_lista_declaraciones(dicc_clases[self.categoria], dicc_clases, cant_tabs)
        
        else:
            return ejemplo_tipo_basico(self.categoria)
    
    def __repr__(self):
        return str(self.categoria) + " " +  str(self.es_primitivo)

class Estructura:
    def __init__(self, declaraciones):
        self.declaraciones = declaraciones
        
    def no_primitivos(self):
        # devuelve una lista con los tipos no primitivos ligados las declaraciones dentro del Struct
        return tipos_no_primitivos_de_una_lista_de_declaraciones(self.declaraciones)
    
    def ejemplo(self, dicc_clases, cant_tabs):
        return ejemplificar_lista_declaraciones(self.declaraciones, dicc_clases, cant_tabs)
    
    def __repr__(self):
        return "Estructura " + str(self.declaraciones)

    

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

def p_start(p):
    'start : tipo'
    dicc_clases = p[1][0]
    clase_principal = p[1][1]
    dependencias_circulares = buscar_dependencias_circulares(dicc_clases)
    dependencias_no_declaradas = buscar_dependencias_no_declaradas(dicc_clases)
    if dependencias_circulares is None:
        if dependencias_no_declaradas is None: 
            ejemplo = crear_ejemplo(dicc_clases, clase_principal)
            p[0] = ejemplo
        else:
            print("ERROR: Hay dependencias sin declarar: " + dependencias_no_declaradas) 
            terminar_parser()
            
    else: # hay dependencias circulares
        ciclo = dependencias_circulares[0][0] + "->" + dependencias_circulares[0][1] + "".join("->"+dependencias_circulares[i][1] for i in range(1,len(dependencias_circulares)))
        print("ERROR: Hay dependencias circulares: " + ciclo)
        terminar_parser()

def p_tipo_novacio(p):
    'tipo : TYPE ID STRUCT LBRACE lista RBRACE tipo'
    dicc = p[7][0]
    if p[2] in dicc:
        print("En linea:caracter = " + str(p.lineno(2)) + ":" + str(p.lexpos(2)) + " :")
        print(f'ERROR: El tipo "{p[2]}" tiene dos declaraciones')
        terminar_parser()
    else:
        dicc[p[2]] = p[5]
        p[0] = (dicc, p[2]) # Al final deberia quedar en p[0][1] la ID del tipo principal.
    
    
def p_tipo_vacio(p):
    'tipo : '
    p[0] = ({}, None) # {} = diccionario vacío.

def p_lista_tipo_basico(p):
    'lista : ID arreglo BASIC_TYPE lista'
    tipo = Tipo(p[3], True)
    decl = Declaracion(p[1], tipo, p[2])
    nombre_cosas_ya_declaradas = [decl.nombre_var for decl in p[4]]
    if p[1] in nombre_cosas_ya_declaradas:
        print("En linea:caracter = " + str(p.lineno(1)) + ":" + str(p.lexpos(1)) + " :")
        print(f'ERROR: El atributo "{p[1]}" tiene dos declaraciones')
        terminar_parser()
    else:
        p[0] = [decl] + p[4]

def p_lista_tipo_estructura_independiente(p):
    'lista : ID arreglo ID lista'
    tipo = Tipo(p[3], False)
    decl = Declaracion(p[1], tipo, p[2])
    nombre_cosas_ya_declaradas = [decl.nombre_var for decl in p[4]]
    if p[1] in nombre_cosas_ya_declaradas:
        print("En linea:caracter = " + str(p.lineno(1)) + ":" + str(p.lexpos(1)) + " :")
        print(f'Error: El atributo "{p[1]}" tiene dos declaraciones')
        terminar_parser()
    else:
        p[0] = [decl] + p[4]

def p_lista_tipo_estructura_dependiente(p):
    'lista : ID arreglo STRUCT LBRACE lista RBRACE lista'
    estructura = Estructura(p[5])
    tipo = Tipo(estructura, False)
    decl = Declaracion(p[1], tipo, p[2])
    nombre_cosas_ya_declaradas = [decl.nombre_var for decl in p[7]]
    if p[1] in nombre_cosas_ya_declaradas:
        print("En linea:caracter = " + str(p.lineno(1)) + ":" + str(p.lexpos(1)) + " :")
        print(f'ERROR: El atributo "{p[1]}" tiene dos declaraciones')
        terminar_parser()
    else:
        p[0] = [decl] + p[7]


def p_lista_vacia(p):
    'lista : '
    p[0] = []

def p_arreglo_novacio(p):
    'arreglo : LBRACK RBRACK arreglo'
    p[0] = p[3] + 1

def p_arreglo_vacio(p):
    'arreglo : '
    p[0] = 0 


class ParsingError(Exception):
    pass

def terminar_parser():
    raise ParsingError

def p_error(p):
    if p is None:
        print("Error al final del programa.")
    else:
        print("En linea:caracter = " + str(p.lineno) + ":" + str(p.lexpos) + " :")
        print("ERROR: No se pudo parsear \'" + str(p.value) + '\'')
    terminar_parser()


parser = yacc.yacc()

def parse(data):
    try:
        p = parser.parse(data)
        return p
    except ParsingError:
        return 'Parsing Error'

def test():
    import sys
    s = sys.stdin.read()
    result = parse(s)
    print(result)

test()
