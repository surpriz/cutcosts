#!/usr/bin/env python3
"""Validate API documentation completeness.

This script checks all API endpoint files to ensure they have
proper documentation including:
- summary parameter
- description parameter
- responses parameter with error codes

Usage:
    python backend/scripts/validate_docs.py
"""

import ast
import sys
from pathlib import Path
from typing import NamedTuple


class DocumentationIssue(NamedTuple):
    """Represents a documentation issue found in a file."""
    file: Path
    endpoint: str
    issue: str


class EndpointInfo(NamedTuple):
    """Information about an endpoint extracted from AST."""
    function_name: str
    http_method: str
    path: str
    has_summary: bool
    has_description: bool
    has_responses: bool
    line_number: int


def extract_decorator_keywords(decorator: ast.expr) -> dict[str, bool]:
    """Extract keyword arguments from a decorator.

    Args:
        decorator: AST node representing a decorator

    Returns:
        Dictionary with has_summary, has_description, has_responses flags
    """
    keywords = {
        "has_summary": False,
        "has_description": False,
        "has_responses": False
    }

    if isinstance(decorator, ast.Call):
        for keyword in decorator.keywords:
            if keyword.arg == "summary":
                keywords["has_summary"] = True
            elif keyword.arg == "description":
                keywords["has_description"] = True
            elif keyword.arg == "responses":
                keywords["has_responses"] = True

    return keywords


def check_endpoint_documentation(file_path: Path) -> list[EndpointInfo]:
    """Check if all endpoints in a file have proper documentation.

    Args:
        file_path: Path to the Python file to check

    Returns:
        List of EndpointInfo objects for all endpoints found
    """
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read(), filename=str(file_path))
    except SyntaxError as e:
        print(f"⚠️  Syntax error in {file_path}: {e}")
        return []

    endpoints = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        # Check if function has router decorators
        for decorator in node.decorator_list:
            # Check for @router.get, @router.post, etc.
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                if isinstance(decorator.func.value, ast.Name) and decorator.func.value.id == "router":
                    http_method = decorator.func.attr.upper()

                    # Extract path from first argument
                    path = "unknown"
                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                        path = decorator.args[0].value

                    # Check for documentation keywords
                    keywords = extract_decorator_keywords(decorator)

                    endpoint = EndpointInfo(
                        function_name=node.name,
                        http_method=http_method,
                        path=path,
                        has_summary=keywords["has_summary"],
                        has_description=keywords["has_description"],
                        has_responses=keywords["has_responses"],
                        line_number=node.lineno
                    )
                    endpoints.append(endpoint)

    return endpoints


def validate_all_routers() -> tuple[list[DocumentationIssue], int]:
    """Validate all router files in the API.

    Returns:
        Tuple of (list of issues found, total number of endpoints checked)
    """
    # Get project root directory
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    routers_dir = backend_dir / "app" / "api" / "v1"

    if not routers_dir.exists():
        print(f"❌ Routers directory not found: {routers_dir}")
        sys.exit(1)

    all_issues = []
    total_endpoints = 0

    # Check all Python files in routers directory
    for router_file in sorted(routers_dir.glob("*.py")):
        if router_file.name == "__init__.py":
            continue

        endpoints = check_endpoint_documentation(router_file)
        total_endpoints += len(endpoints)

        for endpoint in endpoints:
            # Check for missing summary
            if not endpoint.has_summary:
                all_issues.append(DocumentationIssue(
                    file=router_file,
                    endpoint=f"{endpoint.http_method} {endpoint.path}",
                    issue="Missing 'summary' parameter in router decorator"
                ))

            # Check for missing description
            if not endpoint.has_description:
                all_issues.append(DocumentationIssue(
                    file=router_file,
                    endpoint=f"{endpoint.http_method} {endpoint.path}",
                    issue="Missing 'description' parameter (should include code examples)"
                ))

            # Check for missing responses
            if not endpoint.has_responses:
                all_issues.append(DocumentationIssue(
                    file=router_file,
                    endpoint=f"{endpoint.http_method} {endpoint.path}",
                    issue="Missing 'responses' parameter (should document error codes)"
                ))

    return all_issues, total_endpoints


def print_report(issues: list[DocumentationIssue], total_endpoints: int) -> None:
    """Print validation report.

    Args:
        issues: List of documentation issues found
        total_endpoints: Total number of endpoints checked
    """
    print("\n" + "=" * 80)
    print("API DOCUMENTATION VALIDATION REPORT")
    print("=" * 80 + "\n")

    print(f"📊 Total endpoints checked: {total_endpoints}\n")

    if not issues:
        print("✅ All endpoints are properly documented!")
        print("\nDocumentation completeness: 100%")
        return

    print(f"❌ Found {len(issues)} documentation issue(s):\n")

    # Group issues by file
    issues_by_file: dict[Path, list[DocumentationIssue]] = {}
    for issue in issues:
        if issue.file not in issues_by_file:
            issues_by_file[issue.file] = []
        issues_by_file[issue.file].append(issue)

    # Print issues grouped by file
    for file_path, file_issues in sorted(issues_by_file.items()):
        print(f"\n📄 {file_path.name}:")
        for issue in file_issues:
            print(f"  - {issue.endpoint}")
            print(f"    └─ {issue.issue}")

    # Calculate completeness percentage
    total_required_items = total_endpoints * 3  # summary, description, responses
    total_issues_count = len(issues)
    completeness = ((total_required_items - total_issues_count) / total_required_items) * 100

    print(f"\n📈 Documentation completeness: {completeness:.1f}%")
    print("\n" + "=" * 80 + "\n")


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 if all docs are complete, 1 if issues found)
    """
    print("\n🔍 Validating API documentation...")

    issues, total_endpoints = validate_all_routers()

    print_report(issues, total_endpoints)

    if issues:
        print("💡 Tip: Add 'summary', 'description', and 'responses' parameters to router decorators")
        print("   See /backend/app/utils/doc_templates.py for reusable templates\n")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
