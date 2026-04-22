"""
COMPARADOR DE CÓDIGO PYTHON — DETECTOR DE PLAGIO
DESCRIPCIÓN GENERAL
Este programa implementa un detector de similitud entre programas Python.

  Variante A — Texto plano:
    Compara los archivos fuente directamente con difflib.SequenceMatcher.
    Es equivalente al comando `diff` de UNIX sobre texto sin procesar.
    Detecta copias literales o con cambios menores de formato.

  Variante B — Texto preprocesado (tokens):
    1. Tokeniza cada archivo con el módulo `tokenize` de Python (stdlib).
    2. Normaliza los tokens: nombres → 'ID', números → 'NUM', etc.
    3. Compara las secuencias de tokens con difflib.SequenceMatcher.
    4. Encuentra subcadenas comunes largas con Suffix Array + LCP.
    Detecta plagio aunque hayan cambiado nombres, literales o comentarios.

El analizador léxico implementado con PLY es el
equivalente para el lenguaje C de lo que `tokenize` hace para Python.
Ambos cumplen la función de convertir texto fuente en una secuencia
de tokens clasificados por tipo. 

Además de difflib, el programa invoca el comando `diff` de UNIX directamente
a través de subprocess que perimte:
  - Obtener la salida estándar de diff (formato unified) para el reporte.
  - Verificar los resultados de difflib con una herramienta externa probada.
  - Incluir en el reporte HTML la vista diff coloreada (líneas + / -).

MEDIDA DE SIMILITUD

Se proponen y calculan dos medidas complementarias:

  sim_plain  = difflib.SequenceMatcher.ratio()
             = 2 * M / T
             donde M = número de tokens coincidentes, T = total de tokens
             en ambos archivos. Rango: [0, 1].

  sim_tokens = suma de longitudes de subcadenas comunes (SA+LCP)
             / longitud del programa más corto (en tokens)
             Rango: [0, 1]. Esta es la medida propuesta por Baker.

  Umbral de alerta: sim_tokens >= 0.60 → badge rojo (alta similitud)
                    sim_tokens >= 0.30 → badge amarillo (similitud media)
                    sim_tokens <  0.30 → badge verde (baja similitud)

USO DESDE LÍNEA DE COMANDOS

    python comparador_documentado.py <carpeta> [opciones]

    Opciones:
      --top N             Número de pares a reportar (default: 10)
      --min-tokens N      Longitud mínima de subcadena común en tokens
                          (default: 8). Valor más bajo = más sensible.
      --output archivo    Nombre del HTML de salida (default: reporte.html)

    Ejemplo:
      python comparador_documentado.py dataset_python --top 10 --output reporte.html

DEPENDENCIAS
    - Python 3.8+
    - Módulos estándar únicamente: tokenize, difflib, subprocess,
      itertools, html, pathlib, argparse, dataclasses, math, io, os, sys
    - Comando `diff` de UNIX disponible en el PATH (Linux/macOS/WSL)

"""

import os
import sys
import tokenize
import io
import difflib
import subprocess
import html
import argparse
import datetime
from pathlib import Path
from itertools import combinations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# Tipos de token ignorados (no aportan semántica al comparador):
#   COMMENT   → comentarios  (# esto es un comentario)
#   NEWLINE   → fin de línea lógica
#   NL        → línea vacía / continuación
#   INDENT    → incremento de indentación
#   DEDENT    → decremento de indentación
#   ENCODING  → cabecera de encoding (# -*- coding: utf-8 -*-)
#   ENDMARKER → marcador de fin de archivo

IGNORED_TOKEN_TYPES = {
    tokenize.COMMENT,
    tokenize.NEWLINE,
    tokenize.NL,
    tokenize.INDENT,
    tokenize.DEDENT,
    tokenize.ENCODING,
    tokenize.ENDMARKER,
}

# Palabras reservadas de Python — se conservan como están en la normalización
PYTHON_KEYWORDS = {
    'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
    'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
    'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
    'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
    'while', 'with', 'yield'
}


def tokenize_source(source: str) -> List[tokenize.TokenInfo]:
    """
    Convierte un string de código Python en una lista de tokens.

    Usa tokenize.generate_tokens(), que requiere una función readline
    (se simula con io.StringIO). Los tokens de tipo ignorado se filtran
    antes de devolver la lista.

    Parámetros:
        source: string con el código fuente Python completo

    Retorna:
        Lista de TokenInfo. Cada TokenInfo contiene:
          .type    → tipo numérico del token (tokenize.NAME, etc.)
          .string  → texto literal del token ('for', 'i', '42', etc.)
          .start   → (línea, columna) de inicio en el source original
          .end     → (línea, columna) de fin en el source original
    """
    try:
        tokens = list(
            tokenize.generate_tokens(io.StringIO(source).readline)
        )
        return [t for t in tokens if t.type not in IGNORED_TOKEN_TYPES]
    except tokenize.TokenError:
        # Archivo con error de sintaxis — se ignora sin detener el programa
        return []


def normalize_tokens(tokens: List[tokenize.TokenInfo]) -> List[str]:
    """
    Normaliza una lista de tokens para hacer el comparador insensible
    a renombrado de variables y cambio de literales.

    Esta es la etapa de "preprocesamiento" que distingue la Variante B
    de la Variante A. La idea es de Baker (1995): al abstraer los nombres
    concretos, dos programas con la misma estructura pero nombres distintos
    producirán secuencias de tokens idénticas.

    """
    normalized = []
    for tok in tokens:
        if tok.type == tokenize.NAME:
            if tok.string in PYTHON_KEYWORDS:
                normalized.append(tok.string)   # keyword: conservar
            else:
                normalized.append('ID')          # identificador: abstraer
        elif tok.type == tokenize.NUMBER:
            normalized.append('NUM')             # literal numérico: abstraer
        elif tok.type == tokenize.STRING:
            normalized.append('STR')             # literal string: abstraer
        else:
            normalized.append(tok.string)        # operador/puntuación: conservar
    return normalized


# Este módulo invoca `diff` directamente via subprocess y captura su
# salida en formato "unified" (-u), que muestra las líneas añadidas (+),
# eliminadas (-) y de contexto ( ) entre los dos archivos.
#
# El resultado se incluye en el reporte HTML en una sección colapsable,
# permitiendo al docente ver exactamente qué líneas difieren.

def run_unix_diff(file1: str, file2: str) -> str:
    try:
        result = subprocess.run(
            ['diff', '-u', file1, file2],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        # diff retorna código 0 si son iguales, 1 si difieren, 2 si error
        if result.returncode == 2:
            return f"[Error ejecutando diff: {result.stderr}]"
        output = result.stdout
        if not output.strip():
            return "[Los archivos son idénticos según diff]"
        return output
    except FileNotFoundError:
        # `diff` no está en el PATH (Windows sin WSL)
        return "[Herramienta diff de UNIX no disponible en este sistema]"


def colorize_diff(diff_output: str) -> str:
    """
    Convierte la salida de texto de diff a HTML con colores.
    """
    lines = diff_output.splitlines()
    html_lines = []
    for line in lines:
        esc = html.escape(line)
        if line.startswith('+') and not line.startswith('+++'):
            html_lines.append(f'<span style="background:#e6f4ea;color:#1a5e30">{esc}</span>')
        elif line.startswith('-') and not line.startswith('---'):
            html_lines.append(f'<span style="background:#fde8eb;color:#8b0014">{esc}</span>')
        elif line.startswith('@@'):
            html_lines.append(f'<span style="background:#e8f0fe;color:#1a3a8a;font-weight:bold">{esc}</span>')
        elif line.startswith('---') or line.startswith('+++'):
            html_lines.append(f'<span style="color:#555;font-style:italic">{esc}</span>')
        else:
            html_lines.append(f'<span style="color:#444">{esc}</span>')
    return '\n'.join(html_lines)


def compare_plain_text(source1: str, source2: str) -> Tuple[float, List[str]]:
    """
    Variante A: compara dos archivos como texto plano línea por línea.

    Usa difflib.SequenceMatcher sobre las líneas del source original,
    sin ningún preprocesamiento. Es equivalente a ejecutar diff -u y
    medir qué fracción del texto es común.

    Parámetros:
        source1, source2: strings con el código fuente de cada archivo

    Retorna:
        Tupla (similitud, bloques_comunes) donde:
          similitud     = float en [0,1], ratio de SequenceMatcher
          bloques_comunes = lista de strings con las líneas comunes
                            más largas encontradas
    """
    lines1 = source1.splitlines()
    lines2 = source2.splitlines()

    matcher = difflib.SequenceMatcher(None, lines1, lines2)
    ratio = matcher.ratio()

    # Extraer los bloques de líneas que coinciden (matching blocks)
    # get_matching_blocks() retorna lista de (i, j, n): n líneas iguales
    # a partir de lines1[i] y lines2[j]
    common_blocks = []
    for block in matcher.get_matching_blocks():
        i, j, n = block
        if n >= 2:  # solo bloques de 2+ líneas consecutivas
            snippet = ' | '.join(lines1[i:i+min(n,3)])
            if snippet.strip():
                common_blocks.append(snippet[:120])

    return ratio, common_blocks[:8]


def compare_tokens(norm1: List[str], norm2: List[str]) -> float:
    """
    Variante B (parte difflib): compara dos listas de tokens normalizados.

    Al comparar tokens en lugar de texto, el comparador es insensible a:
      - Renombrado de variables (todos son 'ID')
      - Cambio de literales (todos son 'NUM' o 'STR')
      - Cambio de comentarios (eliminados en tokenización)
      - Diferencias de espaciado e indentación

    Parámetros:
        norm1, norm2: listas de tokens normalizados

    Retorna:
        float en [0,1]: ratio de SequenceMatcher sobre tokens
    """
    matcher = difflib.SequenceMatcher(None, norm1, norm2)
    return matcher.ratio()


def build_suffix_array(sequence: List[str]) -> List[int]:
    """
    Construye el Suffix Array de una lista de strings (tokens).

    El Suffix Array es un array de índices [i0, i1, i2, ...] tal que
    sequence[i0:] < sequence[i1:] < sequence[i2:] ... en orden lexicográfico.

    Parámetros:
        sequence: lista de strings (tokens normalizados + separador)

    Retorna:
        Lista de enteros: el Suffix Array
    """
    n = len(sequence)
    if n == 0:
        return []

    # Paso 1: asignar rango inicial a cada token según orden lexicográfico
    # vocabulary mapea cada token único a un entero
    vocabulary = {v: i for i, v in enumerate(sorted(set(sequence)))}
    int_seq = [vocabulary[c] for c in sequence]

    # Ordenamiento inicial: cada sufijo se representa solo por su primer token
    sa = sorted(range(n), key=lambda i: int_seq[i])

    # rank[i] = posición del sufijo que empieza en i dentro del SA actual
    rank = [0] * n
    for pos, idx in enumerate(sa):
        rank[idx] = pos

    # Doubling: en cada iteración comparamos 2*k tokens en lugar de k
    k = 1
    while k < n:
        # Clave de ordenamiento: (rank del primer k-mer, rank del segundo k-mer)
        # El segundo k-mer empieza k posiciones después; si no existe, -1
        def sort_key(i):
            r1 = rank[i]
            r2 = rank[i + k] if i + k < n else -1
            return (r1, r2)

        sa = sorted(range(n), key=sort_key)

        # Recalcular ranks basados en el nuevo ordenamiento
        new_rank = [0] * n
        new_rank[sa[0]] = 0
        for pos in range(1, n):
            new_rank[sa[pos]] = new_rank[sa[pos - 1]]
            if sort_key(sa[pos]) != sort_key(sa[pos - 1]):
                new_rank[sa[pos]] += 1

        rank = new_rank

        # Si todos los ranks son distintos, el SA está completo
        if rank[sa[-1]] == n - 1:
            break

        k *= 2  # duplicar longitud de comparación

    return sa


def build_lcp_array(sequence: List[str], sa: List[int]) -> List[int]:
    """
    Construye el LCP Array usando el algoritmo de Kasai O(n).

    lcp[i] = longitud del prefijo más largo común entre los sufijos
             sa[i-1] y sa[i] en el Suffix Array ordenado.
    lcp[0] = 0 por definición (no hay sufijo anterior).

    El algoritmo de Kasai aprovecha la propiedad:
        Si el sufijo que empieza en i tiene LCP = h con su vecino en el SA,
        entonces el sufijo que empieza en i+1 tiene LCP >= h-1 con su vecino.
    Esto permite calcular todos los LCP en O(n) sin recalcular desde cero.

    Parámetros:
        sequence: la secuencia original (misma que se pasó a build_suffix_array)
        sa:       el Suffix Array construido

    Retorna:
        Lista de enteros: el LCP Array
    """
    n = len(sequence)

    # rank_in_sa[i] = posición del sufijo que empieza en i dentro del SA
    rank_in_sa = [0] * n
    for pos, idx in enumerate(sa):
        rank_in_sa[idx] = pos

    lcp = [0] * n
    h = 0  # LCP actual (se reutiliza entre iteraciones)

    for i in range(n):
        if rank_in_sa[i] > 0:
            # Vecino anterior en el SA ordenado
            prev_in_sa = sa[rank_in_sa[i] - 1]

            # Extender el LCP carácter a carácter desde la posición h
            while (i + h < n and
                   prev_in_sa + h < n and
                   sequence[i + h] == sequence[prev_in_sa + h]):
                h += 1

            lcp[rank_in_sa[i]] = h

            # Por la propiedad de Kasai, el siguiente LCP es >= h-1
            if h > 0:
                h -= 1

    return lcp


def find_common_substrings(seq1: List[str],
                            seq2: List[str],
                            min_len: int = 8) -> List[Tuple[int, int, int]]:
    """
    Encuentra subcadenas comunes de longitud >= min_len entre seq1 y seq2
    usando el Suffix Array + LCP Array de la concatenación.

    Estrategia:
      1. Concatenar: combined = seq1 + ['$SEP$'] + seq2
         El separador '$SEP$' no aparece en ningún token real, garantizando
         que ningún sufijo cruce la frontera entre los dos programas.
      2. Construir SA y LCP de combined.
      3. Recorrer el LCP: si lcp[i] >= min_len y los sufijos sa[i-1] y sa[i]
         provienen de segmentos distintos (uno de seq1, otro de seq2),
         hay una subcadena común de longitud lcp[i].
      4. Eliminar solapamientos: para no contar la misma región dos veces,
         se filtran las subcadenas que se solapan con otras ya encontradas
         (se conserva la más larga de cada par solapado).

    Parámetros:
        seq1, seq2: listas de tokens normalizados de los dos programas
        min_len:    longitud mínima de subcadena para reportar (en tokens)

    Retorna:
        Lista de tuplas (start1, start2, length):
          start1 = índice en seq1 donde empieza la subcadena
          start2 = índice en seq2 donde empieza la subcadena
          length = número de tokens de la subcadena
    """
    SEPARATOR = ['$SEP$']
    combined = seq1 + SEPARATOR + seq2
    n1 = len(seq1)         # separador está en posición n1
    n2 = len(seq2)

    # Construir SA y LCP de la secuencia concatenada
    sa  = build_suffix_array(combined)
    lcp = build_lcp_array(combined, sa)

    results = []
    seen_keys = set()

    for i in range(1, len(combined)):
        length = lcp[i]
        if length < min_len:
            continue

        a = sa[i - 1]
        b = sa[i]

        # Determinar a qué segmento pertenece cada sufijo
        in_seq1_a = (a < n1)
        in_seq1_b = (b < n1)

        # Solo nos interesan pares donde uno está en seq1 y el otro en seq2
        if in_seq1_a == in_seq1_b:
            continue

        # Normalizar: a siempre en seq1, b siempre en seq2
        if not in_seq1_a:
            a, b = b, a

        # Convertir índice en combined a índice local en seq2
        b_local = b - n1 - 1   # -1 por el separador
        if b_local < 0 or b_local >= n2:
            continue

        # Evitar duplicados exactos
        key = (a, b_local, length)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        results.append(key)

    # Ordenar por longitud descendente
    results.sort(key=lambda x: -x[2])

    # Eliminar solapamientos: si dos subcadenas cubren las mismas
    # posiciones en seq1 o seq2, conservar solo la más larga
    used_in_seq1: set = set()
    used_in_seq2: set = set()
    filtered = []

    for start1, start2, length in results:
        positions_in_1 = set(range(start1, start1 + length))
        positions_in_2 = set(range(start2, start2 + length))

        if not (positions_in_1 & used_in_seq1) and \
           not (positions_in_2 & used_in_seq2):
            filtered.append((start1, start2, length))
            used_in_seq1 |= positions_in_1
            used_in_seq2 |= positions_in_2

    return filtered

# medidad de similutid

def similarity_by_suffix_array(seq1: List[str],
                                 seq2: List[str],
                                 matches: List[Tuple[int, int, int]]) -> float:
    """
    Calcula la similitud basada en subcadenas comunes (propuesta de Baker).

    Fórmula:
        similitud = suma(longitud de cada subcadena común)
                    / longitud del programa más corto (en tokens)

    Se divide entre el más corto porque si el programa B es una copia parcial
    de A (más largo), queremos detectar que B es casi completamente igual a
    esa parte de A, aunque A tenga más código adicional.

    El resultado se acota a [0, 1] con min(..., 1.0).

    """
    total_common = sum(length for _, _, length in matches)
    shorter = min(len(seq1), len(seq2))
    if shorter == 0:
        return 0.0
    return min(1.0, total_common / shorter)


@dataclass
class PairResult:
    """
    Almacena todos los resultados de comparar un par de archivos.

    Campos:
        file1, file2          rutas completas a los archivos
        sim_plain             similitud Variante A (texto plano) en [0,1]
        sim_tokens_difflib    similitud Variante B con difflib en [0,1]
        sim_tokens_sa         similitud Variante B con Suffix Array en [0,1]
        common_snippets       fragmentos de tokens comunes para mostrar
        src1_highlighted      HTML del source1 con líneas comunes marcadas
        src2_highlighted      HTML del source2 con líneas comunes marcadas
        diff_output           salida coloreada de diff -u
        n_common_substrings   número de subcadenas comunes encontradas
    """
    file1: str
    file2: str
    sim_plain: float             = 0.0
    sim_tokens_difflib: float    = 0.0
    sim_tokens_sa: float         = 0.0
    common_snippets: List[str]   = field(default_factory=list)
    src1_highlighted: str        = ""
    src2_highlighted: str        = ""
    diff_output: str             = ""
    n_common_substrings: int     = 0


def highlight_by_token_lines(source: str,
                              tokens: List[tokenize.TokenInfo],
                              matched_indices: set) -> str:
    """
    Resalta en el source HTML las líneas que contienen tokens comunes.

    En lugar de resaltar caracteres individuales (complicado por la
    correspondencia token↔posición), se resaltan líneas completas.
    Una línea se resalta si alguno de sus tokens está en matched_indices.

    Parámetros:
        source:          string con el código fuente
        tokens:          lista de TokenInfo del archivo
        matched_indices: conjunto de índices de tokens que son comunes

    Retorna:
        String HTML con las líneas comunes envueltas en <mark>
    """
    # Mapear número de línea → True si contiene token común
    lines_with_match: set = set()
    for idx in matched_indices:
        if idx < len(tokens):
            line_num = tokens[idx].start[0]   # start = (línea, columna)
            lines_with_match.add(line_num)

    output_lines = []
    for line_num, line in enumerate(source.splitlines(), start=1):
        escaped = html.escape(line)
        if line_num in lines_with_match:
            output_lines.append(f'<mark>{escaped}</mark>')
        else:
            output_lines.append(escaped)

    return '\n'.join(output_lines)


def process_pair(file1: str, file2: str,
                 src1: str, src2: str,
                 min_token_len: int = 8) -> PairResult:
    """
    Ejecuta el pipeline completo para un par de archivos.

    Etapas:
      1. Variante A: comparar texto plano con difflib
      2. Tokenizar ambos archivos
      3. Normalizar tokens
      4. Variante B (difflib): comparar tokens normalizados
      5. Variante B (SA): encontrar subcadenas comunes con Suffix Array
      6. Calcular métricas de similitud
      7. Generar HTML resaltado de ambos sources
      8. Ejecutar diff de UNIX y colorizar su salida

    Parámetros:
        file1, file2:   rutas a los archivos
        src1, src2:     contenido de los archivos
        min_token_len:  longitud mínima de subcadena para SA (default: 8)

    Retorna:
        PairResult con todos los resultados
    """
    result = PairResult(file1=file1, file2=file2)

    # ── Etapa 1: Variante A — texto plano ────────────────────────────────────
    sim_plain, plain_common = compare_plain_text(src1, src2)
    result.sim_plain = sim_plain

    # ── Etapa 2 y 3: Tokenización y normalización ─────────────────────────────
    toks1 = tokenize_source(src1)
    toks2 = tokenize_source(src2)
    norm1 = normalize_tokens(toks1)
    norm2 = normalize_tokens(toks2)

    # ── Etapa 4: Variante B (difflib sobre tokens) ────────────────────────────
    result.sim_tokens_difflib = compare_tokens(norm1, norm2)

    # ── Etapa 5: Variante B (Suffix Array) — subcadenas comunes ──────────────
    matches = find_common_substrings(norm1, norm2, min_len=min_token_len)
    result.n_common_substrings = len(matches)

    # ── Etapa 6: Métricas ─────────────────────────────────────────────────────
    result.sim_tokens_sa = similarity_by_suffix_array(norm1, norm2, matches)

    # Extraer snippets de tokens para mostrar en el reporte
    snippets = []
    for start1, start2, length in matches[:12]:
        tokens_preview = norm1[start1: start1 + min(length, 7)]
        snippet = ' '.join(tokens_preview)
        if len(snippet) > 3:
            suffix = '…' if length > 7 else ''
            snippets.append(snippet + suffix)
    result.common_snippets = snippets

    # ── Etapa 7: Resaltado de fuente ──────────────────────────────────────────
    # Recopilar qué índices de tokens están en subcadenas comunes
    matched_in_1: set = set()
    matched_in_2: set = set()
    for start1, start2, length in matches:
        matched_in_1.update(range(start1, start1 + length))
        matched_in_2.update(range(start2, start2 + length))

    result.src1_highlighted = highlight_by_token_lines(src1, toks1, matched_in_1)
    result.src2_highlighted = highlight_by_token_lines(src2, toks2, matched_in_2)

    # ── Etapa 8: diff de UNIX ─────────────────────────────────────────────────
    raw_diff = run_unix_diff(file1, file2)
    result.diff_output = colorize_diff(raw_diff)

    return result

# El reporte HTML muestra para cada par de archivos:
#   - Porcentaje de similitud (Variante A y Variante B)
#   - Los dos sources en paralelo con líneas comunes resaltadas en amarillo
#   - Los fragmentos de tokens comunes detectados por el Suffix Array
#   - La salida coloreada de diff -u (colapsable)

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Detector de Plagio — Reporte</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #f5f6f8; color: #222; font-family: Arial, sans-serif; }}

  header {{ background: #1a56a0; color: #fff; padding: 1.4rem 2rem; }}
  header h1 {{ font-size: 1.5rem; margin: 0 0 .25rem; }}
  header p  {{ font-size: 0.82rem; margin: 0; opacity: .85; font-family: monospace; }}

  .summary {{
    display: flex; gap: 1rem; padding: 1rem 2rem;
    background: #fff; border-bottom: 1px solid #dde; flex-wrap: wrap;
  }}
  .stat {{
    background: #f0f4fa; border: 1px solid #c8d4e8;
    border-radius: 6px; padding: .6rem 1.1rem; min-width: 125px;
  }}
  .stat .label {{ font-size: 0.7rem; color: #666; text-transform: uppercase; letter-spacing: .06em; }}
  .stat .value {{ font-size: 1.6rem; font-weight: 700; color: #1a56a0; }}

  .pairs {{ padding: 1.4rem 2rem; display: flex; flex-direction: column; gap: 1.6rem; }}

  .pair-card {{
    background: #fff; border: 1px solid #d0d8e8;
    border-radius: 8px; overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
  }}
  .pair-header {{
    display: flex; align-items: center; gap: 1rem;
    padding: .9rem 1.3rem; border-bottom: 1px solid #d0d8e8;
    background: #f8fafd; flex-wrap: wrap;
  }}
  .rank {{ font-size: 0.78rem; color: #888; min-width: 22px; font-family: monospace; }}
  .filenames {{ flex: 1; font-size: 0.83rem; font-family: monospace; color: #333; }}
  .filenames .sep {{ color: #aaa; margin: 0 .35rem; }}

  .badge {{ font-size: 0.8rem; font-weight: 700; padding: .22rem .75rem; border-radius: 10px; }}
  .badge.high   {{ background: #fde8eb; color: #b00020; }}
  .badge.medium {{ background: #fef5d8; color: #8a5e00; }}
  .badge.low    {{ background: #e6f4ea; color: #1a6e38; }}

  .metrics {{
    display: flex; gap: .5rem; flex-wrap: wrap;
    padding: .6rem 1.3rem; border-bottom: 1px solid #d0d8e8;
    background: #fafbfd; font-size: 0.78rem; color: #555;
  }}
  .metric-item {{
    background: #eef1f6; border-radius: 4px;
    padding: .2rem .6rem; font-family: monospace;
  }}
  .metric-item b {{ color: #1a56a0; }}

  .code-grid {{ display: grid; grid-template-columns: 1fr 1fr; }}
  .code-pane {{ padding: .9rem 1.1rem; }}
  .code-pane:first-child {{ border-right: 1px solid #d0d8e8; }}
  .code-pane .pane-title {{
    font-size: 0.68rem; color: #888; text-transform: uppercase;
    letter-spacing: .06em; margin-bottom: .5rem; font-family: monospace;
  }}
  pre {{
    font-family: 'Courier New', monospace; font-size: 0.75rem;
    line-height: 1.6; white-space: pre-wrap; word-break: break-all;
    color: #333; max-height: 340px; overflow-y: auto;
    background: #fafbfc; border: 1px solid #e4e8f0;
    border-radius: 4px; padding: .55rem;
  }}
  mark {{ background: #fff3b0; border-bottom: 2px solid #e0b800; color: #4a3800; border-radius: 2px; }}

  .common-list {{
    padding: .6rem 1.3rem .8rem; border-top: 1px solid #d0d8e8;
    display: flex; flex-wrap: wrap; gap: .4rem; align-items: center;
    background: #fafbfc;
  }}
  .common-list .cl-label {{
    font-size: 0.68rem; color: #888; text-transform: uppercase;
    letter-spacing: .06em; font-family: monospace; margin-right: .3rem;
  }}
  .token-chip {{
    font-family: monospace; font-size: 0.7rem;
    background: #eef4ff; border: 1px solid #b8ccee; color: #1e3d8a;
    border-radius: 3px; padding: .1rem .42rem;
    max-width: 230px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }}

  /* Sección diff de UNIX */
  .diff-section {{ border-top: 1px solid #d0d8e8; }}
  .diff-toggle {{
    width: 100%; text-align: left; background: #f0f4fa;
    border: none; cursor: pointer; padding: .6rem 1.3rem;
    font-size: 0.78rem; color: #1a56a0; font-family: monospace;
    border-top: 1px solid #d0d8e8;
  }}
  .diff-toggle:hover {{ background: #e4ecf8; }}
  .diff-content {{
    display: none; padding: .8rem 1.3rem;
    background: #fafbfc;
  }}
  .diff-content.open {{ display: block; }}
  .diff-content pre {{ max-height: 280px; font-size: 0.73rem; }}

  @media (max-width: 680px) {{
    .code-grid {{ grid-template-columns: 1fr; }}
    .code-pane:first-child {{ border-right: none; border-bottom: 1px solid #d0d8e8; }}
    header, .summary, .pairs {{ padding: 1rem; }}
  }}
</style>
</head>
<body>

<header>
  <h1>Detector de Plagio — Programas Python</h1>
  <p>Generado: {timestamp} &nbsp;|&nbsp; Carpeta: {folder} &nbsp;|&nbsp; Archivos analizados: {n_files}</p>
</header>

<div class="summary">
  <div class="stat"><div class="label">Pares comparados</div><div class="value">{n_pairs}</div></div>
  <div class="stat"><div class="label">Pares reportados</div><div class="value">{n_results}</div></div>
  <div class="stat"><div class="label">Mayor similitud (SA)</div><div class="value">{max_sim}%</div></div>
</div>

<div class="pairs">
{pair_cards}
</div>

<script>
  /* Botones para mostrar/ocultar la sección diff de cada par */
  document.querySelectorAll('.diff-toggle').forEach(btn => {{
    btn.addEventListener('click', () => {{
      const content = btn.nextElementSibling;
      content.classList.toggle('open');
      btn.textContent = content.classList.contains('open')
        ? '▲ Ocultar diff -u de UNIX'
        : '▼ Ver diff -u de UNIX';
    }});
  }});
</script>
</body>
</html>
"""

PAIR_CARD_TEMPLATE = """\
<div class="pair-card">
  <div class="pair-header">
    <span class="rank">#{rank}</span>
    <span class="filenames">
      <span title="{file1}">{short1}</span>
      <span class="sep">↔</span>
      <span title="{file2}">{short2}</span>
    </span>
    <span class="badge {badge_class}">{sim_sa:.1f}% (tokens/SA)</span>
  </div>

  <!-- Métricas detalladas: tres variantes de similitud -->
  <div class="metrics">
    <span class="metric-item">Texto plano (difflib): <b>{sim_plain:.1f}%</b></span>
    <span class="metric-item">Tokens (difflib): <b>{sim_tok_dl:.1f}%</b></span>
    <span class="metric-item">Tokens (Suffix Array): <b>{sim_sa:.1f}%</b></span>
    <span class="metric-item">Subcadenas comunes: <b>{n_common}</b></span>
  </div>

  <!-- Código fuente en paralelo con líneas comunes resaltadas -->
  <div class="code-grid">
    <div class="code-pane">
      <div class="pane-title">Archivo 1: {short1}</div>
      <pre>{content1}</pre>
    </div>
    <div class="code-pane">
      <div class="pane-title">Archivo 2: {short2}</div>
      <pre>{content2}</pre>
    </div>
  </div>

  <!-- Fragmentos de tokens comunes detectados por Suffix Array -->
  <div class="common-list">
    <span class="cl-label">Subcadenas comunes ({n_common}):</span>
    {chips}
  </div>

  <!-- Salida de diff -u de UNIX (colapsable) -->
  <div class="diff-section">
    <button class="diff-toggle">▼ Ver diff -u de UNIX</button>
    <div class="diff-content">
      <pre>{diff_html}</pre>
    </div>
  </div>
</div>
"""


def badge_class(score_0_to_1: float) -> str:
    """Determina el color del badge según el nivel de similitud."""
    if score_0_to_1 >= 0.60:
        return "high"      # rojo: alta similitud, probable plagio
    if score_0_to_1 >= 0.30:
        return "medium"    # amarillo: similitud media, revisar
    return "low"           # verde: baja similitud, probablemente OK


def run_pipeline(folder: str,
                 top_n: int = 10,
                 min_token_len: int = 8,
                 output_html: str = "reporte.html") -> None:
    """
    Orquesta el pipeline completo:
      1. Leer todos los archivos .py de la carpeta
      2. Generar todas las combinaciones de pares (n*(n-1)/2)
      3. Procesar cada par con process_pair()
      4. Ordenar por similitud (SA) descendente
      5. Tomar los top_n pares
      6. Generar el reporte HTML

    Parámetros:
        folder:        ruta a la carpeta con los .py
        top_n:         número de pares a incluir en el reporte
        min_token_len: longitud mínima de subcadena para Suffix Array
        output_html:   nombre del archivo HTML de salida
    """
    folder_path = Path(folder)
    py_files = sorted(folder_path.glob("*.py"))

    if len(py_files) < 2:
        print(f"[ERROR] Se necesitan al menos 2 archivos .py en '{folder}'")
        sys.exit(1)

    print(f"[INFO] Archivos encontrados: {len(py_files)}")

    # Leer todos los sources en memoria
    sources: dict = {}
    for f in py_files:
        try:
            sources[str(f)] = f.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            print(f"[WARN] No se pudo leer {f}: {e}")

    # Generar todos los pares posibles
    all_pairs = list(combinations(list(sources.keys()), 2))
    total = len(all_pairs)
    print(f"[INFO] Pares a comparar: {total}")

    # Procesar cada par
    results: List[PairResult] = []
    for i, (f1, f2) in enumerate(all_pairs, 1):
        print(f"  [{i}/{total}] {Path(f1).name} ↔ {Path(f2).name}", end='\r')
        r = process_pair(f1, f2, sources[f1], sources[f2], min_token_len)
        results.append(r)

    # Ordenar por similitud SA descendente y tomar top_n
    results.sort(key=lambda r: r.sim_tokens_sa, reverse=True)
    results = results[:top_n]
    print(f"\n[INFO] Top {len(results)} pares procesados")

    # Construir las tarjetas HTML de cada par
    cards = []
    for rank, r in enumerate(results, 1):
        short1 = Path(r.file1).name
        short2 = Path(r.file2).name

        chips_html = ''.join(
            f'<span class="token-chip" title="{html.escape(s)}">'
            f'{html.escape(s)}</span>'
            for s in r.common_snippets
        ) or '<span class="token-chip">ninguna</span>'

        cards.append(PAIR_CARD_TEMPLATE.format(
            rank=rank,
            file1=html.escape(r.file1),
            file2=html.escape(r.file2),
            short1=html.escape(short1),
            short2=html.escape(short2),
            sim_plain=r.sim_plain * 100,
            sim_tok_dl=r.sim_tokens_difflib * 100,
            sim_sa=r.sim_tokens_sa * 100,
            badge_class=badge_class(r.sim_tokens_sa),
            content1=r.src1_highlighted,
            content2=r.src2_highlighted,
            n_common=r.n_common_substrings,
            chips=chips_html,
            diff_html=r.diff_output,
        ))

    max_sim = f"{results[0].sim_tokens_sa * 100:.1f}" if results else "0.0"

    report = HTML_TEMPLATE.format(
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        folder=html.escape(folder),
        n_files=len(py_files),
        n_pairs=total,
        n_results=len(results),
        max_sim=max_sim,
        pair_cards='\n'.join(cards),
    )

    out_path = Path(output_html)
    out_path.write_text(report, encoding='utf-8')
    print(f"[OK] Reporte generado: {out_path.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Detector de plagio para programas Python.\n"
            "Implementa dos variantes de comparación:\n"
            "  A) Texto plano con difflib\n"
            "  B) Tokens normalizados con difflib + Suffix Array\n"
            "Genera un reporte HTML con las secciones similares resaltadas."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "folder",
        help="Carpeta con los archivos .py a comparar"
    )
    parser.add_argument(
        "--top", type=int, default=10,
        help="Número de pares a reportar (default: 10)"
    )
    parser.add_argument(
        "--min-tokens", type=int, default=8,
        help="Longitud mínima de subcadena común en tokens (default: 8). "
             "Valores menores detectan clones más cortos pero generan más ruido."
    )
    parser.add_argument(
        "--output", default="reporte.html",
        help="Nombre del archivo HTML de salida (default: reporte.html)"
    )

    args = parser.parse_args()
    run_pipeline(args.folder, args.top, args.min_tokens, args.output)
