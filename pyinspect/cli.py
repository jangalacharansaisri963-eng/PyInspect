#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
from pyinspect.analyzer import analyze_project

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def print_banner():
    banner = f"""{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════╗
║          PyInspect v5.0              ║
╚══════════════════════════════════════╝{Colors.ENDC}"""
    print(banner)

def render_dashboard(data: dict):
    print_banner()
    
    # Project Overview Stats
    print(f"\n{Colors.BOLD}Project:{Colors.ENDC} {data.get('project_name', 'Unknown')}")
    print(f"Python files: {Colors.GREEN}{data.get('py_files', 0)}{Colors.ENDC}")
    print(f"Functions:    {Colors.BLUE}{data.get('functions', 0)}{Colors.ENDC}")
    print(f"Classes:      {Colors.BLUE}{data.get('classes', 0)}{Colors.ENDC}")
    print(f"Imports:      {Colors.DIM}{data.get('imports', 0)}{Colors.ENDC}")

    # File Tree Structure
    print(f"\n{Colors.BOLD}📦 Structure{Colors.ENDC}")
    for item in data.get('structure', []):
        print(f" ├── {item}")

    # Warnings Section
    warnings = data.get('warnings', [])
    if warnings:
        print(f"\n{Colors.WARNING}{Colors.BOLD}⚠ Warnings{Colors.ENDC}")
        for warning in warnings:
            print(f" • {warning}")
    else:
        print(f"\n{Colors.GREEN}{Colors.BOLD}⚠ Warnings{Colors.ENDC}\n • No warnings found! Clean code.")

    # Tests Section
    tests = data.get('tests', {})
    if tests.get('found', 0) > 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🧪 Tests{Colors.ENDC}")
        print(f" • {tests.get('found', 0)} tests found")
        print(f" • {Colors.GREEN}{tests.get('passed', 0)} passed{Colors.ENDC}")
        if tests.get('failed', 0) > 0:
            print(f" • {Colors.FAIL}{tests.get('failed', 0)} failed{Colors.ENDC}")
        else:
            print(f" • 0 failed")

    # Complexity Section
    complexity = data.get('complexity', {})
    if complexity:
        print(f"\n{Colors.CYAN}{Colors.BOLD}📊 Complexity{Colors.ENDC}")
        print(f" • Average: {complexity.get('average', 0)}")
        print(f" • Highest: {complexity.get('highest_file', 'N/A')} → {complexity.get('highest_func', 'N/A')} = {complexity.get('highest_score', 0)}")
    print()

def main():
    parser = argparse.ArgumentParser(description="Analyze a Python project with zero dependencies.")
    parser.add_argument("path", nargs="?", default=".", help="Path to the Python project directory")
    args = parser.parse_args()

    target_path = Path(args.path).resolve()
    if not target_path.exists():
        print(f"{Colors.FAIL}Error: Path '{target_path}' does not exist.{Colors.ENDC}")
        sys.exit(1)

    # Run the core AST analyzer engine
    analysis_data = analyze_project(target_path)
    render_dashboard(analysis_data)

if __name__ == "__main__":
    main()
      
