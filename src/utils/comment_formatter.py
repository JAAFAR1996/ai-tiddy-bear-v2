"""from pathlib import Path
from typing import List, Tuple, Optional
import logging
import re.
"""

"""Comment Formatting Utility
Provides standardized comment formatting for consistent code documentation.
"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="utils")


class CommentFormatter:
    """Formats and standardizes comments throughout the codebase.
    Features:
     - Consistent comment styles
     - Proper spacing and alignment
     - Docstring formatting
     - TODO / FIXME standardization.
    """

    def __init__(self) -> None:
        """Initialize comment formatter with standard patterns."""
        # Comment patterns to standardize
        self.patterns = {
            # Single line comments
            "single_line": re.compile(r"^(\s*)#\s*(.+)$"),
            # Multi-line comment blocks
            "block_start": re.compile(r"^(\s*)#\s*(.+)$"),
            # TODO/FIXME comments
            "todo": re.compile(
                r"^(\s*)#\s*(TODO|FIXME|HACK|NOTE|WARNING):\s*(.+)$",
                re.IGNORECASE,
            ),
            # Docstring patterns
            "docstring_start": re.compile(r'^(\s*)(""" |\'\'\')\s*(.*)$'),
            "docstring_end": re.compile(r"^(.*?)(\s*)(\"\"\"|\'\'\')\s*$"),
            # Section headers
            "section_header": re.compile(r"^(\s*)#\s*=+\s*(.+)\s*=+\s*$"),
        }

    def format_single_comment(self, line: str) -> str:
        """Format a single comment line according to standards.

        Args:
            line: Comment line to format
        Returns:
            Formatted comment line

        """
        match = self.patterns["single_line"].match(line)
        if not match:
            return line

        indent, content = match.groups()
        # Ensure single space after #
        formatted_content = content.strip()
        # Capitalize first letter if it's a sentence
        if (
            formatted_content
            and formatted_content[0].islower()
            and not formatted_content.startswith(("http", "ftp", "www"))
        ):
            formatted_content = formatted_content[0].upper() + formatted_content[1:]

        return f"{indent}# {formatted_content}"

    def format_todo_comment(self, line: str) -> str:
        """Format TODO/FIXME comments according to standards.

        Args:
            line: TODO comment line
        Returns:
            Formatted TODO comment

        """
        match = self.patterns["todo"].match(line)
        if not match:
            return line

        indent, tag, content = match.groups()
        # Standardize tags
        tag = tag.upper()
        content = content.strip()
        # Ensure proper format: # TAG: content
        return f"{indent}# {tag}: {content}"

    def format_section_header(self, line: str) -> str:
        """Format section header comments.

        Args:
            line: Section header line
        Returns:
            Formatted section header

        """
        match = self.patterns["section_header"].match(line)
        if not match:
            return line

        indent, title = match.groups()
        title = title.strip()
        # Create standardized section header
        separator = "=" * (len(title) + 4)
        return (
            f"{indent}# {separator}\n{indent}# {title.upper()}\n{indent}# {separator}"
        )

    def format_docstring(self, docstring_lines: List[str]) -> List[str]:
        """Format docstring according to Google/PEP 257 style.

        Args:
            docstring_lines: Lines of the docstring
        Returns:
            Formatted docstring lines

        """
        if not docstring_lines:
            return docstring_lines

        formatted_lines = []
        # Process each line
        for i, line in enumerate(docstring_lines):
            stripped = line.strip()
            # First line should be a summary
            if i == 0:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    quote = stripped[:3]
                    content = stripped[3:].strip()
                    if content and not content.endswith("."):
                        content += "."
                    # Check if it's a one-liner
                    if content and stripped.endswith(quote):
                        # Remove end quotes and add properly
                        content = content[:-3].strip()
                        formatted_lines.append(f'    """{content}"""')
                        continue
                    formatted_lines.append(f'    """{content}')
                    continue
                # Regular first line
                if stripped and not stripped.endswith("."):
                    stripped += "."
                formatted_lines.append(f"    {stripped}")
            # Last line with closing quotes
            elif i == len(docstring_lines) - 1:
                if stripped.endswith('"""') or stripped.endswith("'''"):
                    formatted_lines.append('    """')
                else:
                    formatted_lines.append(f"    {stripped}")
                    formatted_lines.append('    """')
            # Middle lines
            elif stripped:
                formatted_lines.append(f"    {stripped}")
            else:
                formatted_lines.append("")

        return formatted_lines

    def format_file_comments(self, file_content: str) -> str:
        """Format all comments in a file.

        Args:
            file_content: Content of the Python file
        Returns:
            File content with formatted comments

        """
        lines = file_content.splitlines()
        formatted_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Check for TODO/FIXME comments
            if self.patterns["todo"].match(line):
                formatted_lines.append(self.format_todo_comment(line))
            # Check for section headers
            elif self.patterns["section_header"].match(line):
                header_lines = self.format_section_header(line).split("\n")
                formatted_lines.extend(header_lines)
            # Check for regular comments
            elif self.patterns["single_line"].match(line):
                formatted_lines.append(self.format_single_comment(line))
            # Check for docstrings
            elif line.strip().startswith('"""') or line.strip().startswith("'''"):
                docstring_lines = [line]
                i += 1
                # Collect all docstring lines
                while i < len(lines):
                    docstring_lines.append(lines[i])
                    if lines[i].strip().endswith('"""') or lines[i].strip().endswith(
                        "'''",
                    ):
                        break
                    i += 1
                # Format the docstring
                formatted_docstring = self.format_docstring(docstring_lines)
                formatted_lines.extend(formatted_docstring)
            # Regular code line
            else:
                formatted_lines.append(line)
            i += 1

        return "\n".join(formatted_lines)

    def add_missing_docstrings(self, file_content: str) -> str:
        """Add missing docstrings to classes and functions.

        Args:
            file_content: Content of the Python file
        Returns:
            File content with added docstrings

        """
        lines = file_content.splitlines()
        formatted_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            # Check for class or function definition
            if (
                stripped.startswith("class ")
                or stripped.startswith("def ")
                or stripped.startswith("async def ")
            ):
                formatted_lines.append(line)
                # Check if next non-empty line is a docstring
                j = i + 1
                has_docstring = False
                while j < len(lines):
                    next_line = lines[j].strip()
                    if not next_line:
                        j += 1
                        continue
                    if (
                        next_line.startswith('"""')
                        or next_line.startswith("'''")
                        or next_line.startswith('r"""')
                        or next_line.startswith("r'''")
                    ):
                        has_docstring = True
                    break
                # Add placeholder docstring if missing
                if not has_docstring:
                    if stripped.startswith("class "):
                        class_name = stripped.split("(")[0].split()[1]
                        formatted_lines.append('    """')
                        formatted_lines.append(f"    {class_name} class.")
                        formatted_lines.append('    """')
                    elif "def " in stripped:
                        func_name = stripped.split("(")[0].split()[-1]
                        formatted_lines.append('    """')
                        formatted_lines.append(
                            f"    {func_name.replace('_', ' ').title()} function.",
                        )
                        formatted_lines.append('    """')
            else:
                formatted_lines.append(line)
            i += 1

        return "\n".join(formatted_lines)


def format_comments_in_directory(
    directory: Path,
    add_missing_docstrings: bool = False,
) -> None:
    """Format comments in all Python files in a directory.

    Args:
        directory: Directory to process
        add_missing_docstrings: Whether to add missing docstrings

    """
    formatter = CommentFormatter()
    for file_path in directory.rglob("*.py"):
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            # Format comments
            formatted_content = formatter.format_file_comments(content)
            # Add missing docstrings if requested
            if add_missing_docstrings:
                formatted_content = formatter.add_missing_docstrings(formatted_content)
            # Write back formatted content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(formatted_content)
            logger.info(f"Formatted comments in: {file_path}")
        except Exception as e:
            logger.error(f"Error formatting {file_path}: {e}")


if __name__ == "__main__":
    # Example usage - PRODUCTION SAFE: Using proper logging
    logging.basicConfig(level=logging.INFO)
    formatter = CommentFormatter()
    sample_comments = [
        "#this is a comment",
        "# TODO:fix this bug",
        "#= SECTION HEADER =",
        '    """this is a docstring',
        "    with multiple lines",
        '    """',
    ]
    logger.info("Original comments:")
    for comment in sample_comments:
        logger.info(f"  {comment!r}")
    logger.info("\nFormatted comments:")
    for comment in sample_comments:
        if comment.strip().startswith("#"):
            formatted = formatter.format_single_comment(comment)
            logger.info(f"  {formatted!r}")
        elif "TODO" in comment:
            formatted = formatter.format_todo_comment(comment)
            logger.info(f"  {formatted!r}")
