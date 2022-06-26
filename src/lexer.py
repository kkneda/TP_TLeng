import ply.lex as lex # Se importa el modulo con el lexer de ply.

# Diccionario con palabras reservadas:
# TODO: Al importar el lexer la consola tira un warning: "WARNING: Token 'BASIC_TYPE' multiply 
# defined", arreglarlo de ser posible.
reserved = {
	'type' : 'TYPE',
	'struct' : 'STRUCT',
	'int' : 'BASIC_TYPE',
	'bool' : 'BASIC_TYPE',
	'string': 'BASIC_TYPE',
	'float64' : 'BASIC_TYPE',
}

# Lista de nombres de los tokens:
tokens = ['ID', 'LBRACE', 'RBRACE', 'LBRACK', 'RBRACK'] + list(reserved.values())

# Reglas para tokens simples usando solo expresiones regulares:
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACK = r'\['
t_RBRACK = r'\]'

# Regla para token 'ID', con codigo asociado:
def t_ID(t):
	# Un token 'ID' comienza con letra minuscula y puede ser sucedido por cero o mas caracteres 
	# alfanumericos (incluyendo mayusculas):
	r'[a-z][a-zA-Z_0-9]*'
	# Si t.value es palabra reservada le asigna el token correspondiente a t.type, en caso 
	# contrario asigna token 'ID':
	t.type = reserved.get(t.value, 'ID')
	return t

# Regla para contar numero de lineas (podria ser util eventualmente):
def t_newline(t):
	r'\n+'
	# Por cada newline ('\n') se incrementa t.lexer.lineno:
	t.lexer.lineno += len(t.value)

# Caracteres ignorados (espacio y tabulador, 'whitespace'):
t_ignore = ' \t'

def t_error(t):
	# Imprime mensaje de error en caso de detectar caracter que no corresponda con ninguna de las 
	# reglas previas:
	print("Caracter ilegal '%s'" % t.value[0])
	# Se saltea el caracter ilegal y el lexer continua escaneando el siguiente:
	t.lexer.skip(1)

# Se construye el lexer:
lexer = lex.lex()
