import random
import string

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