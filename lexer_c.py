import ply.lex as lex

# Definición de tokens para un lexer de codigos en lenguaje c usando PLY
# En PLY, es mejor separar las palabras reservadas en un diccionario
# en lugar de hacer una lista gigante de "ifs" dentro de t_ID.
reserved = {
    'int': 'INT_KW',
    'float': 'FLOAT_KW',
    'void': 'VOID_KW',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'return': 'RETURN',
    'for': 'FOR'
}

# lista de tokens, incluyendo los tokens de palabras reservadas
# Sumamos nuestros tokens a los valores del diccionario de palabras reservadas
tokens = [
    'ID', 'INT_CONST', 'FLOAT_CONST', 'STRING_LITERAL',
    
    # Operadores Aritméticos y Asignación
    'PLUS', 'MINUS', 'TIMES', 'DIV', 'EQUALS', 'PLUSPLUS', 'MINUSMINUS',
    
    # Operadores Relacionales
    'COMP_EQUALS', 'LESS', 'GREATER', 'LESS_EQ', 'GREATER_EQ',
    
    # Operadores Lógicos
    'AND', 'OR', 'NOT',
    
    # Puntuadores
    'LPAREN', 'RPAREN',     # ( )
    'LBRACE', 'RBRACE',     # { }
    'LBRACKET', 'RBRACKET', # [ ]
    'SEMI', 'COMMA'         # ; ,
] + list(reserved.values())

# regex simples y ply requiere el prefijo t_
# Los tokens compuestos (==, ++) deben se definen ANTES que los simples (=, +).
# PLY los evalúa en el orden en que se declaran usando su longitud.
t_PLUSPLUS    = r'\+\+'
t_MINUSMINUS  = r'--'
t_COMP_EQUALS = r'=='
t_LESS_EQ     = r'<='
t_GREATER_EQ  = r'>='
t_AND         = r'&&'
t_OR          = r'\|\|'

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIV     = r'/'
t_EQUALS  = r'='
t_LESS    = r'<'
t_GREATER = r'>'
t_NOT     = r'!'

t_LPAREN   = r'\('
t_RPAREN   = r'\)'
t_LBRACE   = r'\{'
t_RBRACE   = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMI     = r';'
t_COMMA    = r','

# Caracteres a ignorar 
t_ignore  = ' \t'

# se definen funciones para tokens que requieren procesamiento adicional
# como contar líneas o convertir tipos de datos

# ignora saltos de línea y contar las líneas correctamente
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Comentarios multilínea /* ... */
def t_COMMENT_MULTI(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass

# ignnora los comentarios de una sola línea 
def t_COMMENT(t):
    r'//.*'
    pass # No hace nada, simplemente ignora el comentario

# Ignorar directivas del preprocesador
def t_PREPROCESSOR(t):
    r'\#.*'
    pass

def t_FLOAT_CONST(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INT_CONST(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING_LITERAL(t):
    r'"[^"]*"'
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # Busca si el ID es una palabra reservada y sino lo marca como id 
    t.type = reserved.get(t.value, 'ID')
    return t

# se define una función de error para manejar caracteres ilegales
def t_error(t):
    print(f"Error léxico: Carácter ilegal '{t.value[0]}' en la línea {t.lineno}")
    t.lexer.skip(1)

# se construye el lexer
lexer = lex.lex()

# este codigo es el ejemplo con el que se va a probar el lexer, 
# incluye varias características del lenguaje C para asegurarnos de que el lexer las maneja correctamente.
codigo_prueba = """
#include <stdio.h>

int main() {
    int n = 5;
    int arr[10]; // Probando corchetes
    int i, f;
    i = 1;
    f = 1;
    
    /* Probando comentarios
       multilínea y operadores lógicos */
    if (n > 0 && n <= 100) {
        for (i = 1; i <= n; i++) {
            f = f * i;
        }
    }
    return f;
}
"""

lexer.input(codigo_prueba)

# Imprime los tokens generados por el lexer
if __name__ == "__main__":
    for tok in lexer:
        print(tok)