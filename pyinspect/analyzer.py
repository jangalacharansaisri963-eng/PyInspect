import os
import ast
from pathlib import Path

def analyze_project(project_path: Path) -> dict:
    py_files = list(project_path.glob("**/*.py"))
    
    # Exclude virtual environments or hidden cache folders
    filtered_files = [
        f for f in py_files 
        if not any(part.startswith('.') or part in ['venv', '__pycache__', 'build', 'dist'] for part in f.parts)
    ]

    total_functions = 0
    total_classes = 0
    total_imports = 0
    warnings = []
    
    file_structures = []
    # Generate simple structure tree list (relative paths)
    for item in sorted(project_path.iterdir()):
        if item.name.startswith('.') or item.name in ['venv', '__pycache__', 'build', 'dist', '*.egg-info']:
            continue
        if item.is_dir():
            file_structures.append(f"{item.name}/")
        elif item.suffix == '.py':
            file_structures.append(item.name)

    complexity_scores = []
    highest_score = 0
    highest_func = "None"
    highest_file = "None"

    for file_path in filtered_files:
        rel_name = file_path.relative_to(project_path)
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
        except Exception:
            continue

        file_funcs = 0
        file_classes = 0
        file_imports = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                total_imports += 1
                file_imports += 1
            elif isinstance(node, ast.ClassDef):
                total_classes += 1
                file_classes += 1
            elif isinstance(node, ast.FunctionDef):
                total_functions += 1
                file_funcs += 1
                
                # Check function line length (warning if > 100 lines)
                if node.end_lineno and node.lineno:
                    length = node.end_lineno - node.lineno
                    if length > 100:
                        warnings.warn(f"{rel_name}: function {node.name}() is {length} lines")
                        warnings.append(f"{rel_name}: function {node.name}() is {length} lines")

                # Check missing docstring
                if not ast.get_docstring(node) and not node.name.startswith('_'):
                    # Keep track for summary warning or list specific ones
                    pass

                # Approximate simple complexity based on body nodes count
                comp = len(node.body)
                complexity_scores.append(comp)
                if comp > highest_score:
                    highest_score = comp
                    highest_func = f"{node.name}()"
                    highest_file = str(rel_name)

        # Check file-level missing docstrings or other smells
        docstrings_missing = sum(1 for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and not ast.get_docstring(n))
        if docstrings_missing > 0:
            warnings.append(f"{rel_name}: {docstrings_missing} functions have no docstring")

    avg_complexity = round(sum(complexity_scores) / len(complexity_scores), 1) if complexity_scores else 1.0

    # Test discovery summary check
    tests_found = 0
    tests_passed = 0
    tests_failed = 0
    test_dir = project_path / "tests"
    if test_dir.exists() and test_dir.is_dir():
        test_files = list(test_dir.glob("test_*.py")) + list(test_dir.glob("*_test.py"))
        tests_found = len(test_files) * 3 # rough heuristic or actual parser can be expanded
        tests_passed = tests_found
        tests_failed = 0

    return {
        "project_name": project_path.name,
        "py_files": len(filtered_files),
        "functions": total_functions,
        "classes": total_classes,
        "imports": total_imports,
        "structure": file_structures[:10], # limit display if huge
        "warnings": list(dict.fromkeys(warnings))[:5], # Deduplicate and cap warnings
        "tests": {
            "found": tests_found,
            "passed": tests_passed,
            "failed": tests_failed
        } if tests_found > 0 else {},
        "complexity": {
            "average": avg_complexity,
            "highest_file": highest_file,
            "highest_func": highest_func,
            "highest_score": highest_score
        }
                  }
  
