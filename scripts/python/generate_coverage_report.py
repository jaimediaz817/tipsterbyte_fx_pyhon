#!/usr/bin/env python3
"""
Script para generar reporte detallado de cobertura por archivo
Muestra: cobertura %, líneas no cubiertas, funciones sin test, clases sin test
"""

import xml.etree.ElementTree as ET
import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class FileCoverage:
    """Información de cobertura de un archivo"""

    filename: str
    line_rate: float
    uncovered_lines: List[int]
    total_lines: int
    covered_lines: int


@dataclass
class FunctionInfo:
    """Información de una función"""

    name: str
    line_start: int
    line_end: int
    is_covered: bool


@dataclass
class ClassInfo:
    """Información de una clase"""

    name: str
    line_start: int
    line_end: int
    methods: List[FunctionInfo]


def parse_coverage_xml(coverage_file: str) -> Dict[str, FileCoverage]:
    """
    Parsea el archivo coverage.xml y extrae información por archivo
    """
    tree = ET.parse(coverage_file)
    root = tree.getroot()

    coverage_data = {}

    for package in root.findall(".//package"):
        for cls in package.findall("classes/class"):
            filename = cls.get("filename") or ""
            line_rate = float(cls.get("line-rate", 0))

            # Extraer líneas
            lines = cls.findall("lines/line")
            total_lines = len(lines)
            covered_lines = sum(1 for line in lines if int(line.get("hits") or "0") > 0)
            uncovered_lines = [
                int(line.get("number") or "0")
                for line in lines
                if int(line.get("hits") or "0") == 0
            ]

            coverage_data[filename] = FileCoverage(
                filename=filename,
                line_rate=line_rate,
                uncovered_lines=uncovered_lines,
                total_lines=total_lines,
                covered_lines=covered_lines,
            )

    return coverage_data


def analyze_python_file(filepath: str) -> Tuple[List[FunctionInfo], List[ClassInfo]]:
    """
    Analiza un archivo Python para extraer funciones y clases
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        functions = []
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Es una función
                end_line = node.end_lineno or node.lineno
                func_lines = list(range(node.lineno, end_line + 1))
                functions.append(
                    FunctionInfo(
                        name=node.name,
                        line_start=node.lineno,
                        line_end=end_line,
                        is_covered=False,  # Se actualizará después
                    )
                )

            elif isinstance(node, ast.ClassDef):
                # Es una clase
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        item_end_line = item.end_lineno or item.lineno
                        methods.append(
                            FunctionInfo(
                                name=item.name,
                                line_start=item.lineno,
                                line_end=item_end_line,
                                is_covered=False,
                            )
                        )

                node_end_line = node.end_lineno or node.lineno
                classes.append(
                    ClassInfo(
                        name=node.name,
                        line_start=node.lineno,
                        line_end=node_end_line,
                        methods=methods,
                    )
                )

        return functions, classes

    except Exception as e:
        print(f"  [WARNING] No se pudo analizar {filepath}: {e}")
        return [], []


def check_coverage_for_function(func: FunctionInfo, uncovered_lines: List[int]) -> bool:
    """
    Verifica si una función tiene cobertura
    """
    func_lines = set(range(func.line_start, func.line_end + 1))
    uncovered_set = set(uncovered_lines)

    # Si alguna línea de la función está sin cobertura, la función no está cubierta
    return len(func_lines.intersection(uncovered_set)) == 0


def generate_report(
    coverage_file: str, base_path: str = "backend", threshold: float = 1.0
):
    """
    Genera el reporte completo de cobertura

    Args:
        coverage_file: Ruta al archivo coverage.xml
        base_path: Directorio base del proyecto
        threshold: Umbral mínimo de cobertura (0.0 a 1.0, default: 1.0 = 100%)
    """
    print("=" * 80)
    print("REPORTE DETALLADO DE COBERTURA POR ARCHIVO")
    print("=" * 80)
    print()

    # Parsear coverage.xml
    coverage_data = parse_coverage_xml(coverage_file)

    # Ordenar por cobertura (menor primero)
    sorted_files = sorted(coverage_data.items(), key=lambda x: x[1].line_rate)

    # Archivos con cobertura menor al umbral
    low_coverage_files = [
        (filename, cov) for filename, cov in sorted_files if cov.line_rate < threshold
    ]

    print(f"Total de archivos analizados: {len(coverage_data)}")
    print(f"Umbral de cobertura: {threshold * 100:.0f}%")
    print(f"Archivos con cobertura < {threshold * 100:.0f}%: {len(low_coverage_files)}")
    print()
    print("-" * 80)
    print()

    # Analizar cada archivo con baja cobertura
    for filename, cov in low_coverage_files:
        # Intentar encontrar el archivo en diferentes ubicaciones
        full_path = None
        possible_paths = [
            filename,  # Ruta directa desde raíz
            os.path.join("backend", filename),
            os.path.join("backend", "apps", filename),
            os.path.join("backend", "core", filename),
            os.path.join("backend", "shared", filename),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                full_path = path
                break

        if not full_path or not os.path.exists(full_path):
            print(f"[SKIP] {filename} - Archivo no encontrado")
            continue

        # Analizar funciones y clases
        functions, classes = analyze_python_file(full_path)

        # Determinar qué funciones NO están cubiertas
        uncovered_functions = []
        for func in functions:
            if not check_coverage_for_function(func, cov.uncovered_lines):
                uncovered_functions.append(func)

        # Determinar qué clases tienen métodos sin cobertura
        classes_with_uncovered = []
        for cls in classes:
            uncovered_methods = []
            for method in cls.methods:
                if not check_coverage_for_function(method, cov.uncovered_lines):
                    uncovered_methods.append(method)

            if uncovered_methods:
                classes_with_uncovered.append((cls, uncovered_methods))

        # Mostrar reporte del archivo
        print(f"[FILE] Archivo: {filename}")
        print(f"   [COV] Cobertura: {cov.line_rate * 100:.1f}%")
        print(f"   [LIN] Lineas: {cov.covered_lines}/{cov.total_lines} cubiertas")

        if cov.uncovered_lines:
            # Agrupar líneas consecutivas
            line_groups = group_consecutive_lines(cov.uncovered_lines)
            line_str = ", ".join(
                [f"{g[0]}-{g[-1]}" if len(g) > 1 else str(g[0]) for g in line_groups]
            )
            print(f"   [X] Lineas sin cobertura: {line_str}")

        if uncovered_functions:
            print(f"   [FUNC] Funciones sin testear ({len(uncovered_functions)}):")
            for func in uncovered_functions:
                print(
                    f"      - {func.name}() (lineas {func.line_start}-{func.line_end})"
                )

        if classes_with_uncovered:
            print(
                f"   [CLASS] Clases con metodos sin testear ({len(classes_with_uncovered)}):"
            )
            for cls, methods in classes_with_uncovered:
                print(f"      - {cls.name}:")
                for method in methods:
                    print(
                        f"        * {method.name}() (lineas {method.line_start}-{method.line_end})"
                    )

        if not uncovered_functions and not classes_with_uncovered:
            print(f"   [OK] Todas las funciones tienen cobertura")

        print()
        print("-" * 80)
        print()

    # Resumen final
    print("=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print()

    total_coverage = sum(cov.line_rate for cov in coverage_data.values()) / len(
        coverage_data
    )
    print(f"Cobertura total del proyecto: {total_coverage * 100:.1f}%")
    print()

    # Top 10 archivos con menor cobertura
    print("Top 10 archivos con menor cobertura:")
    for i, (filename, cov) in enumerate(low_coverage_files[:10], 1):
        print(f"  {i:2d}. {filename:<60} {cov.line_rate * 100:5.1f}%")

    print()
    print("=" * 80)


def group_consecutive_lines(lines: List[int]) -> List[List[int]]:
    """
    Agrupa líneas consecutivas
    Ejemplo: [1, 2, 3, 5, 6, 10] -> [[1, 2, 3], [5, 6], [10]]
    """
    if not lines:
        return []

    groups = []
    current_group = [lines[0]]

    for i in range(1, len(lines)):
        if lines[i] == lines[i - 1] + 1:
            current_group.append(lines[i])
        else:
            groups.append(current_group)
            current_group = [lines[i]]

    groups.append(current_group)
    return groups


def main():
    """Función principal"""
    import sys
    import argparse

    # Umbral de cobertura por defecto
    DEFAULT_THRESHOLD = 0.80  # 80%

    parser = argparse.ArgumentParser(
        description="Genera reporte detallado de cobertura por archivo"
    )
    parser.add_argument(
        "--coverage-file",
        default="backend/coverage.xml",
        help="Ruta al archivo coverage.xml (default: backend/coverage.xml)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD * 100,
        help=f"Umbral minimo de cobertura en porcentaje (default: {DEFAULT_THRESHOLD*100}%%)",
    )

    args = parser.parse_args()

    coverage_file = args.coverage_file
    # Convertir porcentaje (0-100) a decimal (0-1)
    threshold = args.threshold / 100.0

    if not os.path.exists(coverage_file):
        print(f"[ERROR] No se encontró el archivo: {coverage_file}")
        print(
            f"[INFO] Ejecuta primero: python -m pytest --cov --cov-report=xml:coverage.xml"
        )
        sys.exit(1)

    generate_report(coverage_file, threshold=threshold)


if __name__ == "__main__":
    main()
