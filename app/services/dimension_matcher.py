"""Service for automatic field-to-dimension matching"""

import logging
from typing import List, Optional

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
        Automatically match a table column to a dimension using hybrid strategy.
        
        Strategy:
        1. Try exact name matching (including case-insensitive)
        2. Try alias matching
        3. Filter by semantic type and try fuzzy matching
        
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
        
        # Step 1: Try exact name match
        dim_id = self.exact_name_match(column.field_name, active_dimensions)
        if dim_id:
            return dim_id
        
        # Step 2: Try alias match
        dim_id = self.alias_match(column.field_name, active_dimensions)
        if dim_id:
            return dim_id
        
        # Step 3: Infer semantic type and filter dimensions
        inferred_semantic_type = self.config.infer_semantic_type(column.logical_type)
        logger.debug(
            f"Inferred semantic type '{inferred_semantic_type}' "
            f"for field '{column.field_name}' (logical_type='{column.logical_type}')"
        )
        
        filtered_dimensions = self.filter_by_semantic_type(
            active_dimensions,
            inferred_semantic_type
        )
        
        # Step 4: Try fuzzy match on filtered dimensions
        dim_id = self.fuzzy_name_match(column.field_name, filtered_dimensions)
        if dim_id:
            return dim_id
        
        # No match found
        logger.info(f"No dimension match found for field '{column.field_name}'")
        return None
