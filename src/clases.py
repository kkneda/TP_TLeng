from ejemplo import ejemplificar_lista_declaraciones, ejemplo_array, ejemplo_tipo_basico, tabulacion
from grafos import tipos_no_primitivos_de_una_lista_de_declaraciones

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
