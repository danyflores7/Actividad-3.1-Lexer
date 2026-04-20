# Manual de Usuario - Analizador Léxico C

Este programa es un analizador léxico para un subconjunto del lenguaje C (Micro-C), desarrollado en Python utilizando la librería `PLY` (Python Lex-Yacc).

## Requisitos
*   Python 3.x
*   Librería `ply`

Para instalar la librería requerida:
```bash
pip install ply
```

## Uso del Analizador
Para ejecutar el analizador con el código de prueba incluido:
```bash
python "Actividad 3.1. Analizador léxico/lexer_c.py"
```

## Estructura del Proyecto
*   `lexer_c.py`: Archivo principal que contiene la lógica del lexer y las expresiones regulares.
*   `Documentacion/`: Contiene la justificación técnica del lenguaje y este manual.

## Ejemplo de Salida
Al ejecutar el programa, se mostrarán los tokens identificados en el formato:
`LexToken(TIPO_TOKEN, VALOR, LINEA, POSICION)`

Ejemplo:
`LexToken(INT_KW, 'int', 4, 43)`
