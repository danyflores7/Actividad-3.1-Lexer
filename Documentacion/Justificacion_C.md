# Documento de Justificación: Alcance del Analizador Léxico para el Lenguaje C

**Referencia al estándar:** ISO/IEC 9899:1999 (C99), Sección 6.4 (Lexical Elements).

## 1. Introducción
El presente documento define y justifica el subconjunto de elementos léxicos del lenguaje de programación C que será procesado por el analizador léxico desarrollado. El objetivo de esta selección es construir un "Micro-C": un analizador lo suficientemente robusto para procesar algoritmos y estructuras de datos comunes, manteniendo una complejidad algorítmica manejable que demuestre la correcta aplicación de expresiones regulares y teoría de autómatas.

## 2. Subconjunto del Lenguaje Seleccionado
Con base en la sección 6.4 del estándar C99, el analizador léxico reconocerá las siguientes categorías de tokens:

*   **Palabras reservadas (Keywords):** `int`, `float`, `void`, `if`, `else`, `while`, `return`, `for`.
*   **Identificadores (Identifiers):** Secuencias de letras, dígitos y guiones bajos que comiencen con una letra o guion bajo.
*   **Constantes (Constants):**
    *   **Enteras:** Secuencias de dígitos.
    *   **Flotantes:** Números con punto decimal fraccionario (sin notación científica).
*   **Literales de Cadena (String Literals):** Cadenas de caracteres encerradas entre comillas dobles "".
*   **Puntuadores y Operadores (Punctuators):**
    *   **Aritméticos y Asignación:** `+`, `-`, `*`, `/`, `=`
    *   **Relacionales:** `==`, `<`, `>`, `<=`, `>=`
    *   **Lógicos:** `&&`, `||`, `!`
    *   **Incremento / Decremento:** `++`, `--`
    *   **Agrupación y Arreglos:** `(`, `)`, `{`, `}`, `[`, `]`, `;`, `,`

**Elementos a ignorar (No generan token):**
*   Espacios en blanco (espacios, tabuladores, saltos de línea).
*   Comentarios de una línea (`//`) y multilínea (`/* ... */`).
*   Directivas del preprocesador (líneas que inician con `#`).

## 3. Justificación de Inclusiones y Exclusiones
La selección del subconjunto anterior obedece a criterios técnicos orientados a equilibrar la funcionalidad del analizador y la viabilidad del desarrollo:

### Justificación de elementos incluidos (Más allá de lo elemental):
*   **Ciclo for y operadores ++ / --:** Se incluyen debido a su altísima frecuencia en la implementación de algoritmos estándar. Son esenciales para iterar sobre estructuras, representando la naturaleza práctica del lenguaje C.
*   **Operadores lógicos booleanos (&&, ||, !):** Se integran para permitir la evaluación de condiciones compuestas en las estructuras de control de flujo (`if`, `while`), una característica omnipresente en la lógica de programación.
*   **Corchetes de arreglos ([, ]):** Se añaden para habilitar el reconocimiento de arreglos unidimensionales, dado que las colecciones de datos son estructuras primitivas indispensables.
*   **Omisión controlada del Preprocesador (#):** Aunque el preprocesador está fuera del alcance (ocurre en la fase de traducción estándar prior a la tokenización), se implementó una regla léica para identificar e ignorar directivas como `#include` o `#define`. Esto permite que el analizador procese archivos de código fuente reales sin arrojar errores en las primeras líneas.

### Justificación de elementos excluidos:
*   **Punteros y Referencias (*, &, ->):** El análisis de punteros introduce ambigüedad léxica intrínseca (por ejemplo, el asterisco `*` puede representar una multiplicación aritmética o una desreferenciación de memoria). Resolver esto requiere contexto a nivel sintáctico que va más allá del alcance de un analizador puramente léxico.
*   **Estructuras de datos complejas (struct, union, enum):** Su implementación aumenta sustancialmente el catálogo de palabras reservadas y puntuadores (como el operador de acceso `.`) sin aportar un nuevo desafío algorítmico al diseño de las expresiones regulares subyacentes.
*   **Notación científica y Hexadecimal:** Se optó por restringir las constantes numéricas a bases decimales simples para evitar la explosión de estados en el autómata finito determinista (AFD) correspondiente a las constantes, priorizando la robustez en los casos de prueba generales.
*   **Operadores a nivel de bits (&, |, <<, >>):** Mantener el conjunto de operadores acotado permite enfocar la validación y pruebas de la herramienta en la correcta identificación y separación de tokens, en lugar de en la gestión exhaustiva de todo el vocabulario de C.
