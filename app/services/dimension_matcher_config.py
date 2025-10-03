"""Configuration for dimension matching"""

from typing import Dict


class DimensionMatchConfig:
    """Configuration for automatic dimension matching"""
    
    # 名称匹配 (Name matching)
    ENABLE_EXACT_NAME_MATCH = True
    ENABLE_ALIAS_MATCH = True
    ENABLE_FUZZY_NAME_MATCH = True
    FUZZY_MATCH_THRESHOLD = 2  # 编辑距离阈值 (Levenshtein distance threshold)
    
    # 语义类型 (Semantic type)
    ENABLE_SEMANTIC_TYPE_FILTER = True
    STRICT_SEMANTIC_TYPE = False  # 是否严格要求语义类型一致
    
    # 逻辑类型到语义类型的映射 (Logical type to semantic type mapping)
    LOGICAL_TYPE_TO_SEMANTIC_TYPE: Dict[str, str] = {
        'bigint': 'ID',
        'int': 'ID',
        'integer': 'ID',
        'long': 'ID',
        'varchar': 'CATEGORY',
        'string': 'CATEGORY',
        'text': 'CATEGORY',
        'date': 'DATE',
        'datetime': 'DATE',
        'timestamp': 'DATE',
    }
    
    @classmethod
    def infer_semantic_type(cls, logical_type: str) -> str:
        """
        Infer semantic type from logical type
        
        Args:
            logical_type: The logical data type (e.g., 'bigint', 'varchar')
            
        Returns:
            Inferred semantic type (e.g., 'ID', 'CATEGORY', 'DATE')
        """
        logical_type_lower = logical_type.lower()
        return cls.LOGICAL_TYPE_TO_SEMANTIC_TYPE.get(logical_type_lower, 'CATEGORY')
