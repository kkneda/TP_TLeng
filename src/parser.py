from grafos import buscar_dependencias_circulares, buscar_dependencias_no_declaradas
from ejemplo import crear_ejemplo
from clases import Declaracion, Tipo, Estructura
import sys
import ply.yacc as yacc

from lexer import tokens

# start -> tipo
# tipo -> TYPE ID STRUCT { lista } tipo | .
# lista -> ID arreglo BASIC_TYPE lista | ID arreglo ID lista | ID arreglo STRUCT { lista } lista | .
# arreglo -> [ ] arreglo | .

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
        print("Falta } en la ultima linea")
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
    s = sys.stdin.read()
    result = parse(s)
    print(result)

test()
