# TP_TLeng

## Idea

Una entrada como:

type persona struct {  
	nombre string  
	edad int  
	nacionalidad pais  
	ventas []float64  
	activo bool  
}

type pais struct {  
	nombre string  
	codigo struct {  
		prefijo string  
		sufijo string  
	}  
}

podría ser tokenizada (mediante lex) como:

TYPE ID STRUCT LBRACE  
	ID BASIC_TYPE  
	ID BASIC_TYPE  
	ID ID  
	ID LBRACK RBRACK BASIC_TYPE  
	ID BASIC_TYPE  
RBRACE

TYPE ID STRUCT LBRACE  
	ID BASIC_TYPE  
	ID STRUCT LBRACE  
		ID BASIC_TYPE  
		ID BASIC_TYPE  
	RBRACE  
RBRACE

Luego, el parser (generado con yacc) se ocuparía de revisar que la forma general de la entrada 
sea correcta con una gramática LALR(1) (incluso SLR(1)) como:

T -> type id struct { L } T | .  
L -> id A basic_type L | id A id L | id struct { L } L | .  
A -> [ ] | .  

(Nota: la gramática es provisoria)

Finalmente, mediante atributos, se podrían revisar cuestiones más específicas dependientes del 
contexto usando reglas semánticas (como que los tipos no primitivos/básicos estén definidos 
dentro de la misma entrada, que no haya referencias circulares, etc.), y generar la cadena 
en formato JSON. Esta vendría a ser la parte verdaderamente difícil.

### Ejemplo de uso de lexer

Desde una terminal con python abierto:

>> import lexer  
>> lexer.lexer.input("type persona struct {    nombre string   edad int        nacionalidad pais       ventas []float64        activo bool }  type pais struct {       nombre string   codigo struct {                 prefijo string          sufijo string   } }") # Uso ejemplo del enunciado.  
>> [token for token in lexer.lexer] # Muestra array con pares <token, valor>.  
