from networkx import DiGraph, is_directed_acyclic_graph
from itertools import chain
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
    # devuelve el ejemplo del tring output de un tipo basico
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
        #AGREGAR DIMENSIONALIDAD
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
        # devuelve la lista de los tipos no primitivos de sus declaraciones
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
        return ejemplificar_lista_declaraciones(self.declaraciones, dicc_clases, cant_tabs + 1)
    
    def __repr__(self):
        return "Estructura " + str(self.declaraciones)

    
def no_hay_dependencias_circulares(dicc):
    # Se arma el grafo de dependencias
    grafo_de_dependencias = DiGraph()
    for nombre, declaraciones in dicc.items():
        grafo_de_dependencias.add_node(nombre)
        vecinos = tipos_no_primitivos_de_una_lista_de_declaraciones(declaraciones)
        aristas = zip([nombre]*len(vecinos), vecinos)
        grafo_de_dependencias.add_edges_from(aristas)
    
    # devuelve verdadero (es decir, que no hay dependencias circulares)
    # si es un grafo de dependencias resultante es aciclico
    return is_directed_acyclic_graph(grafo_de_dependencias)

def todas_las_dependencias_declaradas(dicc):
    for clase, declaraciones in dicc.items():
        dependencias_no_primitivas = tipos_no_primitivos_de_una_lista_de_declaraciones(declaraciones)
        for dependencia_no_primitiva in dependencias_no_primitivas:
            if dependencia_no_primitiva not in dicc:
                return False
    return True

def p_start(p):
    'start : tipo'
    if no_hay_dependencias_circulares(p[1][0]):
        if todas_las_dependencias_declaradas(p[1][0]):
            p[0] = crear_ejemplo(p[1][0], p[1][1])
        else:
            print("FAIL -> Hay dependencias sin declarar")
    else: # hay dependencias circulares
       print("FAIL -> Hay dependencias circulares")
       raise SyntaxError

def p_tipo_novacio(p):
    'tipo : TYPE ID STRUCT LBRACE lista RBRACE tipo'
    dicc = p[7][0]
    if p[2] in dicc:
        print("FAIL -> No se puede declarar dos tipos con el mismo nombre")
        print(f'El tipo "{p[2]}" tiene dos declaraciones')
        raise SyntaxError
    else:
        dicc[p[2]] = p[5]
        p[0] = (dicc, p[2])
    
    
def p_tipo_vacio(p):
    'tipo : '
    p[0] = ({}, None)

def p_lista_tipo_basico(p):
    'lista : ID arreglo BASIC_TYPE lista'
    tipo = Tipo(p[3], True)
    decl = Declaracion(p[1], tipo, p[2])
    nombre_cosas_ya_declaradas = [decl.nombre_var for decl in p[4]]
    if p[1] in nombre_cosas_ya_declaradas:
        print("FAIL -> No se puede declarar dos atributos con el mismo nombre")
        print(f'El atributo "{p[1]}" tiene dos declaraciones')
        raise SyntaxError
    else:
        p[0] = [decl] + p[4]

def p_lista_tipo_estructura_independiente(p):
    'lista : ID arreglo ID lista'
    tipo = Tipo(p[3], False)
    decl = Declaracion(p[1], tipo, p[2])
    nombre_cosas_ya_declaradas = [decl.nombre_var for decl in p[4]]
    if p[1] in nombre_cosas_ya_declaradas:
        print("FAIL -> No se puede declarar dos atributos con el mismo nombre")
        print(f'El atributo "{p[1]}" tiene dos declaraciones')
        raise SyntaxError
    else:
        p[0] = [decl] + p[4]

def p_lista_tipo_estructura_dependiente(p):
    'lista : ID arreglo STRUCT LBRACE lista RBRACE lista'
    estructura = Estructura(p[5])
    tipo = Tipo(estructura, False)
    decl = Declaracion(p[1], tipo, p[2])
    nombre_cosas_ya_declaradas = [decl.nombre_var for decl in p[7]]
    if p[1] in nombre_cosas_ya_declaradas:
        print("FAIL -> No se puede declarar dos atributos con el mismo nombre")
        print(f'El atributo "{p[1]}" tiene dos declaraciones')
        raise SyntaxError
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


def p_error(p):
    print("Syntax error in input!")


parser = yacc.yacc()

def test():
    while True:
        try:
            s = input('calc > ')
        except EOFError:
            break
        if not s: continue
        result = parser.parse(s)
        print(result)

test()
