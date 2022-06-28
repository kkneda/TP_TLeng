import ply.yacc as yacc

from lexer import tokens

# TYPE_DEF -> TYPE TYPE_DECLARE TYPE_DEF | .
# TYPE_DECLARE -> ID TYPE_ELEMENT .
# TYPE_ELEMENT -> [] TYPE_ELEMENT | TYPE_VALUE .
# TYPE_VALUE -> BASIC_TYPE | STRUCT  | ID.
# STRUCT -> struct { MULT_TYPE_DECLARE } .
# MULT_TYPE_DECLARE -> TYPE_DECLARE MULT_TYPE_DECLARE | .

def p_type_def_nonempty(p):
    'type_def : TYPE type_declare type_def'
    pass

def p_type_def_empty(p):
    'type_def : '
    pass

def p_type_declare(p):
    'type_declare : ID type_element'
    pass

def p_type_element_list(p):
    'type_element : LBRACK RBRACK type_element'
    pass

def p_type_element_value(p):
    'type_element : type_value'
    pass

def p_type_value_basic_type(p):
    'type_value : BASIC_TYPE'
    pass

def p_type_value_struct(p):
    'type_value : struct'
    pass

def p_type_value_id(p):
    'type_value : ID'
    pass

def p_struct(p):
    'struct : STRUCT LBRACE mult_type_declare RBRACE'
    pass

def p_mult_type_declare_nonempty(p):
    'mult_type_declare : type_declare mult_type_declare'
    pass

def p_mult_type_declare_empty(p):
    'mult_type_declare : '
    pass

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