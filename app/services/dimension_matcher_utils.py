"""Utility functions for dimension matching"""

from typing import List


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Levenshtein distance (minimum number of edits to transform s1 to s2)
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, or substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def normalize_field_name(field_name: str) -> str:
    """
    Normalize field name for matching (lowercase, remove underscores, etc.)
    
    Args:
        field_name: Original field name
        
    Returns:
        Normalized field name
    """
    # Convert to lowercase
    normalized = field_name.lower()
    # Remove underscores
    normalized = normalized.replace('_', '')
    return normalized


def parse_aliases(alias_str: str) -> List[str]:
    """
    Parse comma-separated alias string into list of normalized aliases.
    
    Args:
        alias_str: Comma-separated alias string
        
    Returns:
        List of normalized alias strings
    """
    if not alias_str:
        return []
    
    aliases = [a.strip().lower() for a in alias_str.split(',') if a.strip()]
    return aliases
