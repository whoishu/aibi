"""Unit tests for dimension matcher"""

import pytest
from app.services.dimension_matcher import DimensionMatcher
from app.services.dimension_matcher_config import DimensionMatchConfig
from app.services.dimension_matcher_utils import (
    levenshtein_distance,
    normalize_field_name,
    parse_aliases,
)
from app.models.metadata import MetaDimension, MetaTableColumn


class TestDimensionMatcherUtils:
    """Test utility functions"""
    
    def test_levenshtein_distance_identical(self):
        """Test Levenshtein distance for identical strings"""
        assert levenshtein_distance("hello", "hello") == 0
    
    def test_levenshtein_distance_single_char_diff(self):
        """Test Levenshtein distance for single character difference"""
        assert levenshtein_distance("hello", "hallo") == 1
    
    def test_levenshtein_distance_insertion(self):
        """Test Levenshtein distance for insertion"""
        assert levenshtein_distance("hello", "helloo") == 1
    
    def test_levenshtein_distance_deletion(self):
        """Test Levenshtein distance for deletion"""
        assert levenshtein_distance("hello", "helo") == 1
    
    def test_levenshtein_distance_multiple_diff(self):
        """Test Levenshtein distance for multiple differences"""
        assert levenshtein_distance("kitten", "sitting") == 3
    
    def test_normalize_field_name(self):
        """Test field name normalization"""
        assert normalize_field_name("User_ID") == "userid"
        assert normalize_field_name("user_name") == "username"
        assert normalize_field_name("OWNER") == "owner"
    
    def test_parse_aliases_empty(self):
        """Test parsing empty aliases"""
        assert parse_aliases("") == []
        assert parse_aliases(None) == []
    
    def test_parse_aliases_single(self):
        """Test parsing single alias"""
        assert parse_aliases("owner") == ["owner"]
    
    def test_parse_aliases_multiple(self):
        """Test parsing multiple aliases"""
        result = parse_aliases("owner, user, creator")
        assert result == ["owner", "user", "creator"]
    
    def test_parse_aliases_with_whitespace(self):
        """Test parsing aliases with extra whitespace"""
        result = parse_aliases("  owner  ,  user  ,  creator  ")
        assert result == ["owner", "user", "creator"]


class TestDimensionMatchConfig:
    """Test configuration class"""
    
    def test_infer_semantic_type_id(self):
        """Test inferring ID semantic type"""
        assert DimensionMatchConfig.infer_semantic_type("bigint") == "ID"
        assert DimensionMatchConfig.infer_semantic_type("int") == "ID"
        assert DimensionMatchConfig.infer_semantic_type("INTEGER") == "ID"
    
    def test_infer_semantic_type_category(self):
        """Test inferring CATEGORY semantic type"""
        assert DimensionMatchConfig.infer_semantic_type("varchar") == "CATEGORY"
        assert DimensionMatchConfig.infer_semantic_type("string") == "CATEGORY"
        assert DimensionMatchConfig.infer_semantic_type("TEXT") == "CATEGORY"
    
    def test_infer_semantic_type_date(self):
        """Test inferring DATE semantic type"""
        assert DimensionMatchConfig.infer_semantic_type("date") == "DATE"
        assert DimensionMatchConfig.infer_semantic_type("datetime") == "DATE"
        assert DimensionMatchConfig.infer_semantic_type("TIMESTAMP") == "DATE"
    
    def test_infer_semantic_type_unknown(self):
        """Test inferring semantic type for unknown types"""
        assert DimensionMatchConfig.infer_semantic_type("unknown_type") == "CATEGORY"


class TestDimensionMatcher:
    """Test dimension matcher service"""
    
    @pytest.fixture
    def matcher(self):
        """Create a dimension matcher instance"""
        return DimensionMatcher()
    
    @pytest.fixture
    def sample_dimensions(self):
        """Create sample dimensions for testing"""
        return [
            MetaDimension(
                id=1,
                name="username",
                verbose_name="用户名",
                alias="owner, user, creator",
                semantic_type="CATEGORY",
                data_type="str",
                dim_type="dim",
                created_by="test",
                updated_by="test",
                status=1,
            ),
            MetaDimension(
                id=2,
                name="user_id",
                verbose_name="用户ID",
                alias="uid",
                semantic_type="ID",
                data_type="str",
                dim_type="dim",
                created_by="test",
                updated_by="test",
                status=1,
            ),
            MetaDimension(
                id=3,
                name="category",
                verbose_name="分类",
                alias="biz_category, cat",
                semantic_type="CATEGORY",
                data_type="str",
                dim_type="dim",
                created_by="test",
                updated_by="test",
                status=1,
            ),
            MetaDimension(
                id=4,
                name="create_time",
                verbose_name="创建时间",
                alias="created_at, created_date",
                semantic_type="DATE",
                data_type="str",
                dim_type="dim",
                created_by="test",
                updated_by="test",
                status=1,
            ),
        ]
    
    def test_exact_name_match(self, matcher, sample_dimensions):
        """Test exact name matching"""
        result = matcher.exact_name_match("username", sample_dimensions)
        assert result == 1
        
        # Case insensitive
        result = matcher.exact_name_match("USERNAME", sample_dimensions)
        assert result == 1
        
        result = matcher.exact_name_match("User_Id", sample_dimensions)
        assert result == 2
    
    def test_exact_name_match_no_match(self, matcher, sample_dimensions):
        """Test exact name matching with no match"""
        result = matcher.exact_name_match("nonexistent", sample_dimensions)
        assert result is None
    
    def test_alias_match(self, matcher, sample_dimensions):
        """Test alias matching"""
        result = matcher.alias_match("owner", sample_dimensions)
        assert result == 1
        
        result = matcher.alias_match("user", sample_dimensions)
        assert result == 1
        
        result = matcher.alias_match("creator", sample_dimensions)
        assert result == 1
        
        result = matcher.alias_match("biz_category", sample_dimensions)
        assert result == 3
    
    def test_alias_match_no_match(self, matcher, sample_dimensions):
        """Test alias matching with no match"""
        result = matcher.alias_match("nonexistent", sample_dimensions)
        assert result is None
    
    def test_fuzzy_name_match(self, matcher, sample_dimensions):
        """Test fuzzy name matching"""
        # Small typo should still match
        result = matcher.fuzzy_name_match("usrname", sample_dimensions)
        assert result == 1
        
        result = matcher.fuzzy_name_match("categry", sample_dimensions)
        assert result == 3
    
    def test_fuzzy_name_match_no_match(self, matcher, sample_dimensions):
        """Test fuzzy name matching with no match (distance too large)"""
        result = matcher.fuzzy_name_match("completely_different", sample_dimensions)
        assert result is None
    
    def test_filter_by_semantic_type(self, matcher, sample_dimensions):
        """Test filtering dimensions by semantic type"""
        result = matcher.filter_by_semantic_type(sample_dimensions, "ID")
        assert len(result) == 1
        assert result[0].id == 2
        
        result = matcher.filter_by_semantic_type(sample_dimensions, "CATEGORY")
        assert len(result) == 2
        assert {d.id for d in result} == {1, 3}
        
        result = matcher.filter_by_semantic_type(sample_dimensions, "DATE")
        assert len(result) == 1
        assert result[0].id == 4
    
    def test_filter_by_semantic_type_no_match(self, matcher, sample_dimensions):
        """Test filtering by semantic type with no matches (non-strict mode)"""
        # In non-strict mode, should return all dimensions if no match
        result = matcher.filter_by_semantic_type(sample_dimensions, "UNKNOWN_TYPE")
        assert len(result) == 4
    
    def test_auto_match_dimension_exact_match(self, matcher, sample_dimensions):
        """Test auto-matching with exact name match"""
        column = MetaTableColumn(
            id=1,
            field_name="username",
            data_type="varchar(100)",
            logical_type="varchar",
            table_id=1,
            created_by="test",
            updated_by="test",
        )
        
        result = matcher.auto_match_dimension(column, sample_dimensions)
        assert result == 1
    
    def test_auto_match_dimension_alias_match(self, matcher, sample_dimensions):
        """Test auto-matching with alias match"""
        column = MetaTableColumn(
            id=1,
            field_name="owner",
            data_type="varchar(100)",
            logical_type="varchar",
            table_id=1,
            created_by="test",
            updated_by="test",
        )
        
        result = matcher.auto_match_dimension(column, sample_dimensions)
        assert result == 1
    
    def test_auto_match_dimension_fuzzy_match(self, matcher, sample_dimensions):
        """Test auto-matching with fuzzy match"""
        column = MetaTableColumn(
            id=1,
            field_name="categry",  # Missing 'o'
            data_type="varchar(100)",
            logical_type="varchar",
            table_id=1,
            created_by="test",
            updated_by="test",
        )
        
        result = matcher.auto_match_dimension(column, sample_dimensions)
        assert result == 3
    
    def test_auto_match_dimension_with_semantic_type_filter(self, matcher, sample_dimensions):
        """Test auto-matching with semantic type filtering"""
        # ID type field should match ID dimension
        column = MetaTableColumn(
            id=1,
            field_name="userid",  # Close to both user_id and username
            data_type="bigint",
            logical_type="bigint",
            table_id=1,
            created_by="test",
            updated_by="test",
        )
        
        result = matcher.auto_match_dimension(column, sample_dimensions)
        # Should match user_id (ID type) not username (CATEGORY type)
        assert result == 2
    
    def test_auto_match_dimension_no_match(self, matcher, sample_dimensions):
        """Test auto-matching with no match found"""
        column = MetaTableColumn(
            id=1,
            field_name="completely_unrelated_field_name",
            data_type="varchar(100)",
            logical_type="varchar",
            table_id=1,
            created_by="test",
            updated_by="test",
        )
        
        result = matcher.auto_match_dimension(column, sample_dimensions)
        assert result is None
    
    def test_auto_match_dimension_inactive_dimensions_filtered(self, matcher, sample_dimensions):
        """Test that inactive dimensions are not matched"""
        # Set all dimensions to inactive
        for dim in sample_dimensions:
            dim.status = 0
        
        column = MetaTableColumn(
            id=1,
            field_name="username",
            data_type="varchar(100)",
            logical_type="varchar",
            table_id=1,
            created_by="test",
            updated_by="test",
        )
        
        result = matcher.auto_match_dimension(column, sample_dimensions)
        assert result is None
    
    def test_auto_match_dimension_empty_dimensions(self, matcher):
        """Test auto-matching with empty dimension list"""
        column = MetaTableColumn(
            id=1,
            field_name="username",
            data_type="varchar(100)",
            logical_type="varchar",
            table_id=1,
            created_by="test",
            updated_by="test",
        )
        
        result = matcher.auto_match_dimension(column, [])
        assert result is None


class TestValueBasedMatching:
    """Test value-based matching functionality (Phase 2)"""
    
    @pytest.fixture
    def matcher(self):
        """Create a dimension matcher instance"""
        return DimensionMatcher()
    
    @pytest.fixture
    def sample_dimensions(self):
        """Create sample dimensions for testing"""
        return [
            MetaDimension(
                id=1,
                name="status",
                verbose_name="状态",
                alias="",
                semantic_type="CATEGORY",
                data_type="str",
                dim_type="dim",
                created_by="test",
                updated_by="test",
                status=1,
            ),
            MetaDimension(
                id=2,
                name="category",
                verbose_name="分类",
                alias="",
                semantic_type="CATEGORY",
                data_type="str",
                dim_type="dim",
                created_by="test",
                updated_by="test",
                status=1,
            ),
        ]
    
    def test_match_by_values_perfect_match(self, matcher, sample_dimensions):
        """Test value matching with perfect overlap"""
        field_values = {"active", "inactive", "pending"}
        dimension_values_map = {
            1: {"active", "inactive", "pending", "archived"},
            2: {"electronics", "books", "clothing"},
        }
        
        result = matcher.match_by_values(
            field_values,
            sample_dimensions,
            dimension_values_map
        )
        
        # Should match dimension 1 (status) with 100% overlap
        assert result == 1
    
    def test_match_by_values_partial_match(self, matcher, sample_dimensions):
        """Test value matching with partial overlap"""
        field_values = {"active", "inactive", "unknown"}
        dimension_values_map = {
            1: {"active", "inactive", "pending"},
            2: {"electronics", "books"},
        }
        
        result = matcher.match_by_values(
            field_values,
            sample_dimensions,
            dimension_values_map
        )
        
        # Should match dimension 1 with 66% overlap (2/3)
        assert result == 1
    
    def test_match_by_values_below_threshold(self, matcher, sample_dimensions):
        """Test value matching below threshold"""
        field_values = {"active", "unknown1", "unknown2", "unknown3", "unknown4"}
        dimension_values_map = {
            1: {"active", "inactive", "pending"},
            2: {"electronics", "books"},
        }
        
        result = matcher.match_by_values(
            field_values,
            sample_dimensions,
            dimension_values_map
        )
        
        # Should not match (20% overlap < 60% threshold)
        assert result is None
    
    def test_match_by_values_no_dimension_values(self, matcher, sample_dimensions):
        """Test value matching when dimensions have no values"""
        field_values = {"active", "inactive"}
        dimension_values_map = {}
        
        result = matcher.match_by_values(
            field_values,
            sample_dimensions,
            dimension_values_map
        )
        
        assert result is None
    
    def test_match_by_values_empty_field_values(self, matcher, sample_dimensions):
        """Test value matching with empty field values"""
        field_values = set()
        dimension_values_map = {
            1: {"active", "inactive"},
        }
        
        result = matcher.match_by_values(
            field_values,
            sample_dimensions,
            dimension_values_map
        )
        
        assert result is None
    
    def test_match_by_values_too_many_unique_values(self, matcher, sample_dimensions):
        """Test that value matching is skipped for high cardinality fields"""
        # Create field with more unique values than threshold
        field_values = {f"value_{i}" for i in range(1000)}
        dimension_values_map = {
            1: field_values,
        }
        
        result = matcher.match_by_values(
            field_values,
            sample_dimensions,
            dimension_values_map
        )
        
        # Should not match because field has too many unique values
        assert result is None
    
    def test_match_by_values_disabled(self, sample_dimensions):
        """Test that value matching can be disabled"""
        from app.services.dimension_matcher_config import DimensionMatchConfig
        
        config = DimensionMatchConfig()
        config.ENABLE_VALUE_MATCH = False
        matcher = DimensionMatcher(config)
        
        field_values = {"active", "inactive", "pending"}
        dimension_values_map = {
            1: {"active", "inactive", "pending"},
        }
        
        result = matcher.match_by_values(
            field_values,
            sample_dimensions,
            dimension_values_map
        )
        
        assert result is None
