"""
SQL Injection Protection & Identifier Sanitizer Utility.
"""

from __future__ import annotations

import re
from typing import Any, Iterable, List, Optional, Set

# Regex pattern for safe database column identifiers (alphanumeric and underscores only)
SAFE_IDENTIFIER_REGEX = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

# Common SQL Injection attack vectors
SQLI_PATTERNS = [
    re.compile(r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|EXEC|UNION|HAVING)\b)", re.IGNORECASE),
    re.compile(r"(--|/\*|\*/|;|@@|char|nchar|varchar|nvarchar)", re.IGNORECASE),
    re.compile(r"(\bOR\b|\bAND\b)\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+", re.IGNORECASE),
]


def is_safe_identifier(identifier: str) -> bool:
    """Validate that a table or column name contains only safe alphanumeric characters."""
    if not identifier:
        return False
    return bool(SAFE_IDENTIFIER_REGEX.match(identifier))


def validate_sort_column(
    sort_field: str,
    allowed_columns: Iterable[str],
    default: str = "id",
) -> str:
    """
    Validate dynamic sort fields against a strict whitelist of allowed column names.
    Prevents SQL injection via dynamic ORDER BY clauses.
    """
    if not sort_field:
        return default

    clean_field = sort_field.strip().lstrip("-").lstrip("+")
    allowed_set = set(allowed_columns)

    if clean_field in allowed_set:
        return sort_field.strip()
    return default


def contains_sqli_patterns(input_str: str) -> bool:
    """Check if input text contains suspicious SQL injection syntax patterns."""
    if not input_str or not isinstance(input_str, str):
        return False
    for pattern in SQLI_PATTERNS:
        if pattern.search(input_str):
            return True
    return False


def sanitize_search_query(query: str, max_length: int = 100) -> str:
    """Sanitize free-text user search queries before passing to ILIKE or text search."""
    if not query:
        return ""
    clean = query.strip()[:max_length]
    # Escape special SQL wildcard characters % and _
    clean = clean.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return clean
