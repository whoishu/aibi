"""Service for automatic field-to-dimension matching"""

import logging
from typing import List, Optional, Set

from app.models.metadata import MetaDimension, MetaTableColumn
from app.services.dimension_matcher_config import DimensionMatchConfig
from app.services.dimension_matcher_utils import (
    levenshtein_distance,
    normalize_field_name,
    parse_aliases,
)

logger = logging.getLogger(__name__)


class DimensionMatcher:
    """
    Service for automatically matching table columns to dimensions.
    
    Implements a hybrid matching strategy:
    1. Exact name matching (精确名称匹配)
    2. Alias matching (别名匹配)
    3. Semantic type filtering + fuzzy name matching (语义类型过滤 + 模糊匹配)
    """
    
    def __init__(self, config: Optional[DimensionMatchConfig] = None):
        """
        Initialize dimension matcher.
        
        Args:
            config: Optional configuration object. Uses defaults if not provided.
        """
        self.config = config or DimensionMatchConfig()
    
    def exact_name_match(
        self,
        field_name: str,
        dimensions: List[MetaDimension]
    ) -> Optional[int]:
        """
        Find dimension with exact name match (case-insensitive).
        
        Args:
            field_name: Column field name to match
            dimensions: List of available dimensions
            
        Returns:
            Dimension ID if exact match found, None otherwise
        """
        if not self.config.ENABLE_EXACT_NAME_MATCH:
            return None
        
        field_name_lower = field_name.lower()
        
        for dim in dimensions:
            if field_name_lower == dim.name.lower():
                logger.info(f"Exact name match: field '{field_name}' -> dimension '{dim.name}' (id={dim.id})")
                return dim.id
        
        return None
    
    def alias_match(
        self,
        field_name: str,
        dimensions: List[MetaDimension]
    ) -> Optional[int]:
        """
        Find dimension where field name matches one of the aliases.
        
        Args:
            field_name: Column field name to match
            dimensions: List of available dimensions
            
        Returns:
            Dimension ID if alias match found, None otherwise
        """
        if not self.config.ENABLE_ALIAS_MATCH:
            return None
        
        field_name_lower = field_name.lower()
        
        for dim in dimensions:
            if dim.alias:
                aliases = parse_aliases(dim.alias)
                if field_name_lower in aliases:
                    logger.info(f"Alias match: field '{field_name}' -> dimension '{dim.name}' (id={dim.id})")
                    return dim.id
        
        return None
    
    def fuzzy_name_match(
        self,
        field_name: str,
        dimensions: List[MetaDimension]
    ) -> Optional[int]:
        """
        Find dimension using fuzzy name matching (Levenshtein distance).
        
        Args:
            field_name: Column field name to match
            dimensions: List of available dimensions
            
        Returns:
            Dimension ID if fuzzy match found within threshold, None otherwise
        """
        if not self.config.ENABLE_FUZZY_NAME_MATCH:
            return None
        
        if not dimensions:
            return None
        
        # Normalize field name for comparison
        normalized_field = normalize_field_name(field_name)
        
        best_match_id = None
        min_distance = float('inf')
        
        for dim in dimensions:
            # Compare with dimension name
            normalized_dim = normalize_field_name(dim.name)
            distance = levenshtein_distance(normalized_field, normalized_dim)
            
            if distance < min_distance:
                min_distance = distance
                best_match_id = dim.id
            
            # Also check aliases if available
            if dim.alias:
                aliases = parse_aliases(dim.alias)
                for alias in aliases:
                    normalized_alias = normalize_field_name(alias)
                    distance = levenshtein_distance(normalized_field, normalized_alias)
                    if distance < min_distance:
                        min_distance = distance
                        best_match_id = dim.id
        
        # Only return match if within threshold
        if min_distance <= self.config.FUZZY_MATCH_THRESHOLD:
            matched_dim = next((d for d in dimensions if d.id == best_match_id), None)
            if matched_dim:
                logger.info(
                    f"Fuzzy match: field '{field_name}' -> dimension '{matched_dim.name}' "
                    f"(id={best_match_id}, distance={min_distance})"
                )
            return best_match_id
        
        return None
    
    def filter_by_semantic_type(
        self,
        dimensions: List[MetaDimension],
        semantic_type: str
    ) -> List[MetaDimension]:
        """
        Filter dimensions by semantic type.
        
        Args:
            dimensions: List of dimensions to filter
            semantic_type: Target semantic type
            
        Returns:
            Filtered list of dimensions matching semantic type
        """
        if not self.config.ENABLE_SEMANTIC_TYPE_FILTER:
            return dimensions
        
        # If strict mode, only return exact matches
        if self.config.STRICT_SEMANTIC_TYPE:
            return [dim for dim in dimensions if dim.semantic_type == semantic_type]
        
        # In non-strict mode, prefer matching but allow all if no matches
        filtered = [dim for dim in dimensions if dim.semantic_type == semantic_type]
        if filtered:
            return filtered
        
        # No matches found, return all (non-strict mode)
        return dimensions
    
    def auto_match_dimension(
        self,
        column: MetaTableColumn,
        dimensions: List[MetaDimension]
    ) -> Optional[int]:
        """
        Automatically match a table column to a dimension using hybrid strategy with scoring.
        
        Strategy:
        Each matching method assigns a score to candidate dimensions:
        - Exact name match: 100 points
        - Alias match: 90 points
        - Fuzzy match: 70-90 points (based on edit distance)
        - Semantic type match: +10 bonus points
        
        Returns the dimension with the highest score above threshold.
        
        Args:
            column: Table column to match
            dimensions: List of available dimensions to match against
            
        Returns:
            Matched dimension ID, or None if no match found
        """
        if not dimensions:
            logger.warning(f"No dimensions available for matching column '{column.field_name}'")
            return None
        
        # Filter to only active dimensions (status=1)
        active_dimensions = [dim for dim in dimensions if dim.status == 1]
        if not active_dimensions:
            logger.warning("No active dimensions available for matching")
            return None
        
        # Infer semantic type for bonus scoring
        inferred_semantic_type = self.config.infer_semantic_type(column.logical_type)
        logger.debug(
            f"Inferred semantic type '{inferred_semantic_type}' "
            f"for field '{column.field_name}' (logical_type='{column.logical_type}')"
        )
        
        # Score each dimension
        dimension_scores = []
        
        for dim in active_dimensions:
            score = 0
            match_type = None
            
            # Check exact name match (100 points)
            if column.field_name.lower() == dim.name.lower():
                score = 100
                match_type = "exact_name"
            
            # Check alias match (90 points)
            elif dim.alias:
                aliases = parse_aliases(dim.alias)
                if column.field_name.lower() in aliases:
                    score = 90
                    match_type = "alias"
            
            # Check fuzzy match (70-90 points based on distance)
            if score == 0 and self.config.ENABLE_FUZZY_NAME_MATCH:
                normalized_field = normalize_field_name(column.field_name)
                normalized_dim = normalize_field_name(dim.name)
                distance = levenshtein_distance(normalized_field, normalized_dim)
                
                if distance <= self.config.FUZZY_MATCH_THRESHOLD:
                    # Score inversely proportional to distance
                    # distance 0 = 90, distance 1 = 80, distance 2 = 70
                    score = 90 - (distance * 10)
                    match_type = f"fuzzy_name (distance={distance})"
                
                # Also check fuzzy match with aliases
                if score == 0 and dim.alias:
                    aliases = parse_aliases(dim.alias)
                    for alias in aliases:
                        normalized_alias = normalize_field_name(alias)
                        distance = levenshtein_distance(normalized_field, normalized_alias)
                        if distance <= self.config.FUZZY_MATCH_THRESHOLD:
                            alias_score = 85 - (distance * 10)  # Slightly lower than name fuzzy
                            if alias_score > score:
                                score = alias_score
                                match_type = f"fuzzy_alias (distance={distance})"
            
            # Add semantic type bonus (10 points)
            if score > 0 and dim.semantic_type == inferred_semantic_type:
                score += 10
                match_type += " +semantic_type"
            
            if score > 0:
                dimension_scores.append({
                    'dimension_id': dim.id,
                    'dimension_name': dim.name,
                    'score': score,
                    'match_type': match_type
                })
        
        # Sort by score (descending) and return the best match
        if dimension_scores:
            dimension_scores.sort(key=lambda x: x['score'], reverse=True)
            best_match = dimension_scores[0]
            
            logger.info(
                f"Matched column '{column.field_name}' to dimension '{best_match['dimension_name']}' "
                f"(id={best_match['dimension_id']}, score={best_match['score']}, "
                f"type={best_match['match_type']})"
            )
            
            # Log other candidates for debugging
            if len(dimension_scores) > 1:
                other_candidates = dimension_scores[1:4]  # Show top 3 alternatives
                logger.debug(
                    f"Other candidates for '{column.field_name}': " +
                    ", ".join([
                        f"{c['dimension_name']}({c['score']})"
                        for c in other_candidates
                    ])
                )
            
            return best_match['dimension_id']
        
        # No match found
        logger.info(f"No dimension match found for field '{column.field_name}'")
        return None
    
    def match_by_values(
        self,
        field_values: Set[str],
        dimensions: List[MetaDimension],
        dimension_values_map: dict
    ) -> Optional[int]:
        """
        Find dimension by comparing field unique values with dimension values.
        
        This method samples unique values from a field and compares them with
        known dimension values to find the best match based on overlap ratio.
        
        Args:
            field_values: Set of unique values from the field
            dimensions: List of available dimensions
            dimension_values_map: Dictionary mapping dimension_id to set of values
            
        Returns:
            Dimension ID if match found with ratio above threshold, None otherwise
        """
        if not self.config.ENABLE_VALUE_MATCH:
            return None
        
        if not field_values:
            logger.debug("No field values provided for value matching")
            return None
        
        # Check if field has too many unique values
        if len(field_values) > self.config.MAX_UNIQUE_VALUES_FOR_VALUE_MATCH:
            logger.debug(
                f"Field has {len(field_values)} unique values, "
                f"exceeding threshold {self.config.MAX_UNIQUE_VALUES_FOR_VALUE_MATCH}"
            )
            return None
        
        best_match_id = None
        max_ratio = 0.0
        
        for dim in dimensions:
            if dim.id not in dimension_values_map:
                continue
            
            dim_values = dimension_values_map[dim.id]
            if not dim_values:
                continue
            
            # Calculate overlap
            intersection = field_values & dim_values
            overlap_ratio = len(intersection) / len(field_values) if len(field_values) > 0 else 0
            
            if overlap_ratio > max_ratio and overlap_ratio >= self.config.VALUE_MATCH_THRESHOLD:
                max_ratio = overlap_ratio
                best_match_id = dim.id
                logger.debug(
                    f"Value match candidate: dimension '{dim.name}' "
                    f"(id={dim.id}, ratio={overlap_ratio:.2f})"
                )
        
        if best_match_id:
            matched_dim = next((d for d in dimensions if d.id == best_match_id), None)
            if matched_dim:
                logger.info(
                    f"Value match: field values → dimension '{matched_dim.name}' "
                    f"(id={best_match_id}, ratio={max_ratio:.2f})"
                )
        
        return best_match_id
