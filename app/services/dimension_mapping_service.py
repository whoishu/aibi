"""Service for automatic dimension mapping to table columns"""

import logging
from typing import Any, Dict, List, Optional, Tuple
import re

try:
    import Levenshtein
    HAS_LEVENSHTEIN = True
except ImportError:
    HAS_LEVENSHTEIN = False

from sqlmodel import Session, select
from app.models.metadata import MetaDimension, MetaTableColumn


logger = logging.getLogger(__name__)


class DimensionMappingService:
    """Service for automatically mapping table columns to dimensions"""
    
    def __init__(self, session: Session):
        """Initialize dimension mapping service
        
        Args:
            session: Database session
        """
        self.session = session
    
    def _normalize_name(self, name: str) -> str:
        """Normalize field/dimension name for comparison
        
        Handles case insensitivity, underscores, and camelCase
        
        Args:
            name: Field or dimension name
            
        Returns:
            Normalized name in lowercase
        """
        # Convert camelCase to snake_case
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        # Convert to lowercase and remove extra spaces/underscores
        name = name.lower().strip().replace('-', '_')
        return name
    
    def _exact_match_score(self, field_name: str, dimension_name: str) -> float:
        """Calculate exact match score
        
        Args:
            field_name: Table column field name
            dimension_name: Dimension name
            
        Returns:
            Score between 0.0 and 1.0
        """
        norm_field = self._normalize_name(field_name)
        norm_dim = self._normalize_name(dimension_name)
        
        if norm_field == norm_dim:
            return 1.0
        return 0.0
    
    def _alias_match_score(self, field_name: str, dimension: MetaDimension) -> float:
        """Calculate alias match score
        
        Args:
            field_name: Table column field name
            dimension: Dimension object with alias field
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not dimension.alias:
            return 0.0
        
        norm_field = self._normalize_name(field_name)
        aliases = [self._normalize_name(a.strip()) for a in dimension.alias.split(',')]
        
        if norm_field in aliases:
            return 0.95  # Slightly lower than exact match
        return 0.0
    
    def _fuzzy_match_score(self, field_name: str, dimension_name: str) -> float:
        """Calculate fuzzy match score using Levenshtein distance
        
        Args:
            field_name: Table column field name
            dimension_name: Dimension name
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not HAS_LEVENSHTEIN:
            return 0.0
        
        norm_field = self._normalize_name(field_name)
        norm_dim = self._normalize_name(dimension_name)
        
        # Calculate similarity ratio
        distance = Levenshtein.distance(norm_field, norm_dim)
        max_len = max(len(norm_field), len(norm_dim))
        
        if max_len == 0:
            return 0.0
        
        similarity = 1.0 - (distance / max_len)
        
        # Only consider matches with high similarity (>= 0.7)
        if similarity >= 0.7:
            return similarity * 0.8  # Scale down fuzzy matches
        return 0.0
    
    def _semantic_type_match(
        self, 
        column_logical_type: str, 
        dimension_semantic_type: str
    ) -> bool:
        """Check if semantic types are compatible
        
        Args:
            column_logical_type: Logical type of the column
            dimension_semantic_type: Semantic type of the dimension
            
        Returns:
            True if types are compatible
        """
        # Simple matching logic - can be extended
        type_mappings = {
            'ID': ['int', 'bigint', 'varchar', 'string', 'text'],
            'DATE': ['date', 'datetime', 'timestamp', 'time'],
            'CATEGORY': ['varchar', 'string', 'text', 'int', 'enum']
        }
        
        logical_type_lower = column_logical_type.lower()
        compatible_types = type_mappings.get(dimension_semantic_type, [])
        
        return any(ct in logical_type_lower for ct in compatible_types)
    
    def _value_based_match_score(
        self,
        field_values: List[Any],
        dimension: MetaDimension,
        dimension_values: Optional[List[Any]] = None
    ) -> float:
        """Calculate value-based match score
        
        Compares unique values from the field with dimension's possible values
        
        Args:
            field_values: Unique values from the table column
            dimension: Dimension object
            dimension_values: Optional list of known dimension values
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not field_values or not dimension_values:
            return 0.0
        
        # Convert to sets for intersection calculation
        field_set = set(str(v).lower() for v in field_values if v is not None)
        dim_set = set(str(v).lower() for v in dimension_values if v is not None)
        
        if not field_set or not dim_set:
            return 0.0
        
        # Calculate overlap ratio
        intersection = field_set.intersection(dim_set)
        overlap_ratio = len(intersection) / len(field_set)
        
        # High overlap indicates strong match
        if overlap_ratio >= 0.6:
            return overlap_ratio
        
        return 0.0
    
    def calculate_dimension_scores(
        self,
        column: MetaTableColumn,
        field_values: Optional[List[Any]] = None,
        dimension_values_map: Optional[Dict[int, List[Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Calculate matching scores for all candidate dimensions
        
        Args:
            column: Table column to map
            field_values: Optional unique values from this column
            dimension_values_map: Optional mapping of dimension_id to their possible values
            
        Returns:
            List of candidate dimensions with scores, sorted by total score
        """
        # Get all active dimensions
        statement = select(MetaDimension).where(MetaDimension.status == 1)
        dimensions = self.session.exec(statement).all()
        
        candidates = []
        
        for dimension in dimensions:
            scores = {
                'exact_match': self._exact_match_score(column.field_name, dimension.name),
                'alias_match': self._alias_match_score(column.field_name, dimension),
                'fuzzy_match': self._fuzzy_match_score(column.field_name, dimension.name),
                'value_match': 0.0,
                'semantic_match': 0.0
            }
            
            # Check semantic type compatibility
            if self._semantic_type_match(column.logical_type, dimension.semantic_type):
                scores['semantic_match'] = 0.3  # Bonus for semantic compatibility
            
            # Calculate value-based match if values are provided
            if field_values and dimension_values_map and dimension.id in dimension_values_map:
                dim_values = dimension_values_map.get(dimension.id, [])
                scores['value_match'] = self._value_based_match_score(
                    field_values, dimension, dim_values
                )
            
            # Calculate weighted total score
            # Value match has highest weight when available
            weights = {
                'exact_match': 1.0,
                'alias_match': 0.95,
                'fuzzy_match': 0.5,
                'value_match': 1.2,  # Highest weight
                'semantic_match': 0.2  # Supplementary
            }
            
            total_score = sum(scores[key] * weights[key] for key in scores)
            
            # Only include candidates with meaningful scores (> 0.3)
            if total_score > 0.3:
                candidates.append({
                    'dimension_id': dimension.id,
                    'dimension_name': dimension.name,
                    'dimension_verbose_name': dimension.verbose_name,
                    'dimension_semantic_type': dimension.semantic_type,
                    'total_score': total_score,
                    'scores': scores,
                    'confidence': self._calculate_confidence(total_score, scores)
                })
        
        # Sort by total score descending
        candidates.sort(key=lambda x: x['total_score'], reverse=True)
        
        return candidates
    
    def _calculate_confidence(self, total_score: float, scores: Dict[str, float]) -> str:
        """Calculate confidence level based on scores
        
        Args:
            total_score: Total weighted score
            scores: Individual score components
            
        Returns:
            Confidence level: 'high', 'medium', or 'low'
        """
        # High confidence: exact/alias match or high value match
        if scores['exact_match'] > 0 or scores['alias_match'] > 0:
            return 'high'
        
        if scores['value_match'] >= 0.8:
            return 'high'
        
        # Medium confidence: good fuzzy match + semantic match or good value match
        if scores['fuzzy_match'] >= 0.8 and scores['semantic_match'] > 0:
            return 'medium'
        
        if scores['value_match'] >= 0.6:
            return 'medium'
        
        # Otherwise low confidence
        return 'low'
    
    def suggest_dimension_mappings(
        self,
        table_id: int,
        max_candidates: int = 5,
        min_score: float = 0.3
    ) -> Dict[int, List[Dict[str, Any]]]:
        """Suggest dimension mappings for all columns in a table
        
        Args:
            table_id: ID of the table to analyze
            max_candidates: Maximum number of candidates per column
            min_score: Minimum score threshold
            
        Returns:
            Dictionary mapping column_id to list of candidate dimensions
        """
        # Get all columns for this table without existing dimension mapping
        statement = select(MetaTableColumn).where(
            MetaTableColumn.table_id == table_id,
            MetaTableColumn.dimension_id == None,  # noqa: E711
            MetaTableColumn.status == 1
        )
        columns = self.session.exec(statement).all()
        
        result = {}
        
        for column in columns:
            candidates = self.calculate_dimension_scores(column)
            
            # Filter by min_score and limit to max_candidates
            filtered = [c for c in candidates if c['total_score'] >= min_score][:max_candidates]
            
            if filtered:
                result[column.id] = {
                    'column_id': column.id,
                    'field_name': column.field_name,
                    'description': column.description,
                    'logical_type': column.logical_type,
                    'candidates': filtered
                }
        
        return result
    
    def apply_dimension_mapping(
        self,
        column_id: int,
        dimension_id: int,
        updated_by: str
    ) -> bool:
        """Apply a dimension mapping to a column
        
        Args:
            column_id: ID of the column
            dimension_id: ID of the dimension to map
            updated_by: User applying the mapping
            
        Returns:
            True if successful, False otherwise
        """
        column = self.session.get(MetaTableColumn, column_id)
        
        if not column:
            logger.error(f"Column {column_id} not found")
            return False
        
        dimension = self.session.get(MetaDimension, dimension_id)
        
        if not dimension:
            logger.error(f"Dimension {dimension_id} not found")
            return False
        
        column.dimension_id = dimension_id
        column.updated_by = updated_by
        
        self.session.add(column)
        self.session.commit()
        self.session.refresh(column)
        
        logger.info(f"Mapped column {column_id} to dimension {dimension_id}")
        return True
