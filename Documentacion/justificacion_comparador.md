# Documento de Justificación: Comparador de Código Python

**Referencia teórica:** Baker, B. S. (1995). *A program for identifying duplicate code.* Computing Science and Statistics, 27, 49–57.  
**Biblioteca de comparación:** `difflib` (Python Standard Library, `SequenceMatcher`).  
**Herramienta de verificación:** `diff -u` (UNIX unified diff).

---

## 1. Introducción

El presente documento justifica el diseño e implementación de un comparador de similitud entre programas Python, orientado a la detección de plagio académico. La solución implementa dos variantes de comparación basadas en las ideas del artículo de Baker (1995), cuya premisa central es que comparar código a nivel de *tokens* en lugar de texto plano permite detectar tipos de similitud estructural que una comparación textual ingenua es incapaz de identificar.

Para ello, se adopta la taxonomía de clones de código ampliamente reconocida en la literatura, que clasifica las similitudes entre programas en cuatro tipos según su grado de abstracción:

| Tipo 1 | Copia literal, idéntica o con mínimas diferencias de formato | Mismo archivo, distintos espacios |
| Tipo 2 | Misma estructura, nombres de variables y literales cambiados | Renombrar `n` por `numero`** |
| Tipo 3 | Fragmentos copiados con modificaciones, adiciones o eliminaciones | Copiar función y agregar un `print` |
| Tipo 4 | Mismo comportamiento, implementación distinta | Reescritura completa |

Esta solución cubre robustamente los **Tipos 1 y 2**, que son los más frecuentes en contextos académicos.

## 2. Variantes Implementadas

### Variante A — Comparación de Texto Plano (difflib sobre source)

**Descripción:** Se aplica `difflib.SequenceMatcher` directamente sobre las líneas del archivo fuente sin ningún preprocesamiento. Es funcionalmente equivalente al comando `diff -u` de UNIX, que se integra también como herramienta de verificación externa.

**Métrica:** `ratio() = 2M / T`, donde M es el número de líneas coincidentes y T el total de líneas en ambos archivos.

**Qué detecta:** Clones de **Tipo 1**. Copias literales o con cambios menores de formato, espaciado o comentarios simples.

**Limitación:** Al operar sobre caracteres crudos, cualquier renombrado de variable rompe la coincidencia. Un alumno que cambie todos los nombres de variables produce una similitud cercana a 0% en esta variante, aunque la estructura lógica del programa sea idéntica.

---

### Variante B — Comparación de Tokens Normalizados (difflib + Suffix Array sobre tokens)

**Descripción:** Antes de comparar, cada archivo se somete a un pipeline de dos etapas:

#### Etapa 1 — Análisis léxico con `tokenize`

Se utiliza el módulo `tokenize` de la biblioteca estándar de Python, que es el mismo tokenizador que usa el intérprete CPython internamente. Esta elección es equivalente al uso de PLY para el analizador léxico de C implementado en la entrega anterior: ambos cumplen la misma función (convertir texto fuente en tokens clasificados por tipo), pero cada uno está diseñado para la gramática de su lenguaje objetivo. `tokenize` reconoce correctamente construcciones propias de Python como indentación significativa, f-strings y decoradores.

Los tokens de tipo no semántico se descartan antes de la comparación:

| `COMMENT` | No aporta lógica del programa |
| `NEWLINE`, `NL` | Diferencias de formato irrelevantes |
| `INDENT`, `DEDENT` | El reformateo no debe afectar la similitud |
| `ENCODING`, `ENDMARKER` | Metadatos del archivo |

#### Etapa 2 — Normalización

Se abstraen los elementos que un alumno puede cambiar superficialmente sin alterar la lógica del programa:

```
Identificadores (variables, funciones, clases)  →  'ID'
Literales numéricos (42, 3.14, 0xFF)            →  'NUM'
Literales de cadena ("hola", f"...", 'mundo')   →  'STR'
Palabras reservadas (for, if, def, return...)   →  se conservan
Operadores y puntuación (+, ==, (, :, ...)      →  se conservan
```

Esta normalización es precisamente lo que Baker (1995) propone: al abstraer los nombres concretos, dos programas con la misma estructura pero vocabulario distinto producen secuencias de tokens idénticas o muy similares, revelando la copia estructural.

**Ejemplo**

```
# Archivo original          →   Tokens normalizados
def factorial(n):           →   def ID ( ID ) :
    if n <= 1:              →       if ID <= NUM :
        return 1            →           return NUM
    return n * factorial    →       return ID * ID

# Archivo plagiado          →   Tokens normalizados 
def calcular(numero):       →   def ID ( ID ) :
    if numero <= 1:         →       if ID <= NUM :
        return 1            →           return NUM
    return numero*calcular  →       return ID * ID
```

Sobre estos tokens normalizados se aplican dos técnicas complementarias:

- **`difflib.SequenceMatcher`** sobre la secuencia de tokens: detecta coincidencias en el mismo orden (Tipos 1 y 2).
- **Suffix Array + LCP Array**: detecta subcadenas comunes independientemente de su posición relativa, permitiendo identificar funciones copiadas aunque hayan sido reordenadas dentro del archivo (acercamiento al Tipo 3).

**Métrica:** `similitud = Σ longitudes de subcadenas comunes / longitud del programa más corto`. Se divide entre el más corto porque si B es una copia parcial de A, queremos detectar que B es casi completamente igual a esa parte de A aunque A tenga código adicional.

---

## 3. Justificación de la selección del Suffix Array

Nos dimos cuenta que Suffix Array tiee:

- **Eficiencia en memoria:** El Suffix Array es una representación compacta (array de enteros) frente al Suffix Tree (estructura de árbol con punteros). Para comparar programas de varios cientos de líneas, la diferencia es significativa.
- **Detección de múltiples bloques:** A diferencia del LCS, que encuentra una sola subcadena común óptima, el Suffix Array + LCP permite encontrar todas las subcadenas comunes de longitud ≥ k en un solo recorrido del LCP Array. Esto es clave cuando un alumno copió múltiples funciones dispersas en el archivo.
- **Continuidad con implementaciones previas:** El algoritmo de construcción por doubling O(n log n) se basa en la misma referencia teórica (cp-algorithms.com) utilizada en la implementación de Suffix Array en C++ de la entrega anterior, garantizando coherencia metodológica en el proyecto.

---

## 4. Rol de diff de UNIX

El comando `diff -u` se integra como **herramienta de verificación externa** por las razones que indica el enunciado: permite una inspección visual directa de las diferencias línea a línea, independiente de las métricas calculadas por el comparador. Su salida en formato *unified* (líneas `+`/`-` con contexto) es el estándar de la industria para reportar diferencias entre archivos de texto y es familiar para cualquier desarrollador o docente que revise el reporte.

