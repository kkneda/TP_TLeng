from networkx import DiGraph, is_directed_acyclic_graph
from functools import reduce
from itertools import chain
import ply.yacc as yacc

from lexer import tokens

# start -> tipo
# tipo -> TYPE ID STRUCT { lista } tipo | .
# lista -> ID arreglo BASIC_TYPE lista | ID arreglo ID lista | ID arreglo STRUCT { lista } lista | .
# arreglo -> [ ] arreglo | .



class Declaracion:
    def __init__(self, nombre_var, tipo):
        self.nombre_var = nombre_var
        self.tipo = tipo
        
    def tipos_no_primitivos(self):
        return self.tipo.no_primitivos()
    
    def __repr__(self):
        return str(self.nombre_var) + " " +  str(self.tipo)

class Tipo:
    def __init__(self, categoria, es_primitivo, dimension):
        self.categoria = categoria
        self.es_primitivo = es_primitivo
        self.dimension = dimension
        
    def no_primitivos(self):
        if isinstance(self.categoria, Struct):
            return self.categoria.no_primitivos()
        elif not self.es_primitivo:
            return [self.categoria]
        else:
            return []
    
    def __repr__(self):
        return str(self.categoria) + " " +  str(self.es_primitivo) + " " + str(self.dimension)

class Struct:
    def __init__(self, declaraciones):
        self.declaraciones = declaraciones
        
    def no_primitivos(self):
        return chain(
            *map(
                lambda x: x.tipos_no_primitivos(),
                self.declaraciones,
            )
        )
    
    def __repr__(self):
        return "Struct " + str(self.declaraciones)
    
def hay_dependencias_circulares(dicc: dict):
    grafo_de_dependencias = DiGraph()
    for nombre, declaraciones in dicc.items():
        grafo_de_dependencias.add_node(nombre)
        vecinos = set(
            chain(
                *map(
                    lambda x: x.tipos_no_primitivos(),
                    declaraciones
                )
            )
        )
        aristas = zip([nombre]*len(vecinos), vecinos)
        grafo_de_dependencias.add_edges_from(aristas)
    
    return not is_directed_acyclic_graph(grafo_de_dependencias)

def p_start(p):
    'start : tipo'
    if hay_dependencias_circulares(p[1]):
        print("FAIL -> Hay dependencias circulares")
        raise SyntaxError
    else:
        p[0] = p[1]

def p_tipo_novacio(p):
    'tipo : TYPE ID STRUCT LBRACE lista RBRACE tipo'
    dicc = p[7]
    if p[2] in dicc:
        print("FAIL -> No se puede declarar dos tipos con los mismos nombre_var")
        print(f'El tipo "{p[2]}" tiene dos declaraciones')
        raise SyntaxError
    else:
        dicc[p[2]] = p[5]
        p[0] = dicc
    
    
def p_tipo_vacio(p):
    'tipo : '
    p[0] = {}

def p_lista_tipo_basico(p):
    'lista : ID arreglo BASIC_TYPE lista'
    tipo = Tipo(p[3], True,p[2])
    decl = Declaracion(p[1], tipo)
    nombre_cosas_ya_declaradas = [decl.nombre_var for decl in p[4]]
    if p[1] in nombre_cosas_ya_declaradas:
        print("FAIL -> No se puede declarar dos atributos iguales")
        print(f'El atributo "{p[1]}" tiene dos declaraciones')
        raise SyntaxError
    else:
        p[0] = [decl] + p[4]

def p_lista_tipo_estructura_independiente(p):
    'lista : ID arreglo ID lista'
    tipo = Tipo(p[3], False, p[2])
    decl = Declaracion(p[1], tipo)
    nombre_cosas_ya_declaradas = [decl.nombre_var for decl in p[4]]
    if p[1] in nombre_cosas_ya_declaradas:
        print("FAIL -> No se puede declarar dos atributos iguales")
        print(f'El atributo "{p[1]}" tiene dos declaraciones')
        raise SyntaxError
    else:
        p[0] = [decl] + p[4]

def p_lista_tipo_estructura_dependiente(p):
    'lista : ID arreglo STRUCT LBRACE lista RBRACE lista'
    estructura = Struct(p[5])
    tipo = Tipo(estructura, False, p[2])
    decl = Declaracion(p[1], tipo)
    nombre_cosas_ya_declaradas = [decl.nombre_var for decl in p[7]]
    if p[1] in nombre_cosas_ya_declaradas:
        print("FAIL -> No se puede declarar dos atributos iguales")
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
