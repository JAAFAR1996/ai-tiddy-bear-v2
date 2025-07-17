"""
from pathlib import Path
from typing import List, Tuple, Dict
import logging
import os
import ast
"""

"""Find Long Functions Utility
Identifies functions and methods that exceed specified line limits.
"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="utils")


class FunctionAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze function lengths."""

    def __init__(self, max_lines: int = 50) -> None:
        """Initialize analyzer with maximum line limit."""
        self.max_lines = max_lines
        self.long_functions: List[Tuple[str, int, int, str]] = []
        self.current_file = ""

    def visit_FunctionDef(self, node) -> None:
        """Visit function definition nodes."""
        self._check_function_length(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node) -> None:
        """Visit async function definition nodes."""
        self._check_function_length(node)
        self.generic_visit(node)

    def _check_function_length(self, node):
        """Check if function exceeds line limit."""
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            func_length = node.end_lineno - node.lineno + 1
            if func_length > self.max_lines:
                self.long_functions.append((
                    self.current_file,
                    node.lineno,
                    func_length,
                    node.name
                ))

    def analyze_file(self, file_path: str) -> None:
        """Analyze a single Python file."""
        self.current_file = file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            self.visit(tree)
        except (SyntaxError, UnicodeDecodeError) as e:
            logger.error(f"Error parsing {file_path}: {e}")


def find_long_functions(directory: str, max_lines: int = 50) -> List[Tuple[str, int, int, str]]:
    """
    Find all functions exceeding the line limit in a directory.
    Args:
        directory: Directory to search
        max_lines: Maximum allowed lines per function
    Returns:
        List of tuples: (file_path, line_number, function_length, function_name)
    """
    analyzer = FunctionAnalyzer(max_lines)
    # Find all Python files
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                analyzer.analyze_file(file_path)
    return analyzer.long_functions


def print_long_functions_report(directory: str, max_lines: int = 50) -> None:
    """Print a report of long functions."""
    long_functions = find_long_functions(directory, max_lines)
    if not long_functions:
        logger.info(f"✅ No functions found exceeding {max_lines} lines!")
        return

    logger.info(f"🔍 Found {len(long_functions)} functions exceeding {max_lines} lines:\n")
    # Sort by length (longest first)
    long_functions.sort(key=lambda x: x[2], reverse=True)
    for file_path, line_num, length, func_name in long_functions:
        relative_path = os.path.relpath(file_path, directory)
        logger.info(f"📄 {relative_path}:{line_num}")
        logger.info(f"   Function: {func_name}")
        logger.info(f"   Length: {length} lines")
        logger.info("")


def suggest_refactoring(file_path: str, function_name: str, start_line: int) -> List[str]:
    """Suggest refactoring strategies for a long function."""
    suggestions = [
        f"Consider breaking down {function_name}() into smaller functions:",
        "• Extract logical blocks into separate helper methods",
        "• Use the Single Responsibility Principle",
        "• Look for repeated code that can be extracted",
        "• Consider using strategy pattern for complex conditionals",
        "• Extract validation logic into separate validators",
        "• Move error handling to separate functions"
    ]
    return suggestions


if __name__ == "__main__":
    # Configure logging for development
    logging.basicConfig(level=logging.INFO)
    # Example usage
    backend_dir = "/mnt/c/Users/jaafa/Desktop/5555/ai-teddy/backend/src"
    logger.info("=== Long Functions Analysis ===\n")
    print_long_functions_report(backend_dir, max_lines=50)
    # Also check for very long functions (100+ lines)
    logger.info("\n=== Very Long Functions (100+ lines) ===\n")
    print_long_functions_report(backend_dir, max_lines=100)