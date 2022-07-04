import ply.yacc as yacc

from lexer import tokens

# tipo -> TYPE ID STRUCT { lista } tipo | .
# lista -> ID arreglo BASIC_TYPE lista | ID arreglo ID lista | ID arreglo STRUCT { lista } lista | .
# arreglo -> [ ] arreglo | .



class Declaracion:
    def __init__(self, nombre_var, tipo):
        self.nombre_var = nombre_var
        self.tipo = tipo
    def __repr__(self):
        return str(self.nombre_var) + " " +  str(self.tipo)

class Tipo:
    def __init__(self, categoria, es_primitivo, dimension):
        self.categoria = categoria
        self.es_primitivo = es_primitivo
        self.dimension = dimension
    def __repr__(self):
        return str(self.categoria) + " " +  str(self.es_primitivo) + " " + str(self.dimension)

class Struct:
    def __init__(self, declaraciones):
        self.declaraciones = declaraciones
    def __repr__(self):
        return "Struct " +  str(self.declaraciones)

def p_tipo_novacio(p):
    'tipo : TYPE ID STRUCT LBRACE lista RBRACE tipo'
    dicc = p[7]
    if p[2] in dicc:
        print("FAIL -> Definiste dos veces lo mismo")
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
    p[0] = [decl] + p[4]

def p_lista_tipo_estructura_independiente(p):
    'lista : ID arreglo ID lista'
    tipo = Tipo(p[3], False, p[2])
    decl = Declaracion(p[1], tipo)
    p[0] = [decl] + p[4]

def p_lista_tipo_estructura_dependiente(p):
    'lista : ID arreglo STRUCT LBRACE lista RBRACE lista'
    estructura = Struct(p[5])
    tipo = Tipo(estructura, False, p[2])
    decl = Declaracion(p[1], tipo)
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

#test()
