"""Unit tests for dimension mapping service"""

import pytest
from sqlmodel import Session, create_engine, SQLModel

from app.services.dimension_mapping_service import DimensionMappingService
from app.models.metadata import (
    MetaDimension,
    MetaTableColumn,
    MetaTable,
    MetaDatabase,
    MetaDomain
)


@pytest.fixture
def session():
    """Create an in-memory database session for testing"""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session


@pytest.fixture
def setup_test_data(session):
    """Setup test dimensions and table columns"""
    # Create test database
    db = MetaDatabase(
        name="test_db",
        db_type="postgresql",
        created_by="test",
        updated_by="test"
    )
    session.add(db)
    session.commit()
    session.refresh(db)
    
    # Create test domain
    domain = MetaDomain(
        name="test_domain",
        created_by="test",
        updated_by="test"
    )
    session.add(domain)
    session.commit()
    session.refresh(domain)
    
    # Create test table
    table = MetaTable(
        name="test_table",
        full_name="test_db.public.test_table",
        verbose_name="测试表",
        database_id=db.id,
        domain_id=domain.id,
        created_by="test",
        updated_by="test"
    )
    session.add(table)
    session.commit()
    session.refresh(table)
    
    # Create test dimensions
    dimensions = [
        MetaDimension(
            name="user_id",
            verbose_name="用户ID",
            semantic_type="ID",
            alias="uid,userId",
            status=1,
            created_by="test",
            updated_by="test"
        ),
        MetaDimension(
            name="category",
            verbose_name="类别",
            semantic_type="CATEGORY",
            alias="cat,type",
            status=1,
            created_by="test",
            updated_by="test"
        ),
        MetaDimension(
            name="business_category",
            verbose_name="业务类别",
            semantic_type="CATEGORY",
            alias="biz_category,biz_cat",
            status=1,
            created_by="test",
            updated_by="test"
        ),
        MetaDimension(
            name="created_date",
            verbose_name="创建日期",
            semantic_type="DATE",
            status=1,
            created_by="test",
            updated_by="test"
        ),
    ]
    
    for dim in dimensions:
        session.add(dim)
    session.commit()
    
    for dim in dimensions:
        session.refresh(dim)
    
    # Create test columns
    columns = [
        MetaTableColumn(
            field_name="user_id",
            data_type="bigint",
            logical_type="bigint",
            table_id=table.id,
            status=1,
            created_by="test",
            updated_by="test"
        ),
        MetaTableColumn(
            field_name="userId",
            data_type="varchar",
            logical_type="varchar",
            table_id=table.id,
            status=1,
            created_by="test",
            updated_by="test"
        ),
        MetaTableColumn(
            field_name="biz_category",
            data_type="varchar",
            logical_type="varchar",
            table_id=table.id,
            status=1,
            created_by="test",
            updated_by="test"
        ),
        MetaTableColumn(
            field_name="categry",  # Typo - fuzzy match
            data_type="varchar",
            logical_type="varchar",
            table_id=table.id,
            status=1,
            created_by="test",
            updated_by="test"
        ),
        MetaTableColumn(
            field_name="create_date",
            data_type="date",
            logical_type="date",
            table_id=table.id,
            status=1,
            created_by="test",
            updated_by="test"
        ),
    ]
    
    for col in columns:
        session.add(col)
    session.commit()
    
    for col in columns:
        session.refresh(col)
    
    return {
        'table': table,
        'dimensions': dimensions,
        'columns': columns,
        'db': db,
        'domain': domain
    }


@pytest.mark.unit
def test_normalize_name(session):
    """Test name normalization"""
    service = DimensionMappingService(session)
    
    assert service._normalize_name("user_id") == "user_id"
    assert service._normalize_name("userId") == "user_id"
    assert service._normalize_name("UserID") == "user_id"
    assert service._normalize_name("USER-ID") == "user_id"
    assert service._normalize_name("  user_id  ") == "user_id"


@pytest.mark.unit
def test_exact_match_score(session, setup_test_data):
    """Test exact match scoring"""
    service = DimensionMappingService(session)
    data = setup_test_data
    
    # Test exact match
    score = service._exact_match_score("user_id", "user_id")
    assert score == 1.0
    
    # Test case-insensitive match
    score = service._exact_match_score("userId", "user_id")
    assert score == 1.0
    
    # Test no match
    score = service._exact_match_score("product_id", "user_id")
    assert score == 0.0


@pytest.mark.unit
def test_alias_match_score(session, setup_test_data):
    """Test alias match scoring"""
    service = DimensionMappingService(session)
    data = setup_test_data
    
    user_dim = data['dimensions'][0]
    
    # Test alias match
    score = service._alias_match_score("uid", user_dim)
    assert score == 0.95
    
    # Test case-insensitive alias match
    score = service._alias_match_score("UID", user_dim)
    assert score == 0.95
    
    # Test no match
    score = service._alias_match_score("product_id", user_dim)
    assert score == 0.0


@pytest.mark.unit
def test_fuzzy_match_score(session):
    """Test fuzzy match scoring"""
    service = DimensionMappingService(session)
    
    try:
        import Levenshtein
        
        # Test high similarity
        score = service._fuzzy_match_score("categry", "category")
        assert score > 0.5
        
        # Test low similarity
        score = service._fuzzy_match_score("user_id", "product_name")
        assert score == 0.0
    except ImportError:
        # Skip if Levenshtein not available
        pytest.skip("Levenshtein library not available")


@pytest.mark.unit
def test_semantic_type_match(session):
    """Test semantic type matching"""
    service = DimensionMappingService(session)
    
    # Test ID type
    assert service._semantic_type_match("bigint", "ID") is True
    assert service._semantic_type_match("varchar", "ID") is True
    assert service._semantic_type_match("date", "ID") is False
    
    # Test DATE type
    assert service._semantic_type_match("date", "DATE") is True
    assert service._semantic_type_match("datetime", "DATE") is True
    assert service._semantic_type_match("varchar", "DATE") is False
    
    # Test CATEGORY type
    assert service._semantic_type_match("varchar", "CATEGORY") is True
    assert service._semantic_type_match("string", "CATEGORY") is True
    assert service._semantic_type_match("int", "CATEGORY") is True


@pytest.mark.unit
def test_value_based_match_score(session, setup_test_data):
    """Test value-based matching"""
    service = DimensionMappingService(session)
    data = setup_test_data
    
    category_dim = data['dimensions'][1]
    
    # Test high overlap
    field_values = ["electronics", "books", "clothing"]
    dim_values = ["electronics", "books", "clothing", "toys"]
    score = service._value_based_match_score(field_values, category_dim, dim_values)
    assert score >= 0.75
    
    # Test medium overlap
    field_values = ["electronics", "books", "sports"]
    dim_values = ["electronics", "books", "clothing", "toys"]
    score = service._value_based_match_score(field_values, category_dim, dim_values)
    assert 0.6 <= score < 0.75
    
    # Test low overlap
    field_values = ["a", "b", "c"]
    dim_values = ["x", "y", "z"]
    score = service._value_based_match_score(field_values, category_dim, dim_values)
    assert score == 0.0


@pytest.mark.unit
def test_calculate_dimension_scores_exact_match(session, setup_test_data):
    """Test dimension score calculation with exact match"""
    service = DimensionMappingService(session)
    data = setup_test_data
    
    # Column with exact name match
    user_id_col = data['columns'][0]
    candidates = service.calculate_dimension_scores(user_id_col)
    
    assert len(candidates) > 0
    # First candidate should be user_id dimension with high score
    assert candidates[0]['dimension_name'] == 'user_id'
    assert candidates[0]['confidence'] == 'high'
    assert candidates[0]['total_score'] >= 1.0


@pytest.mark.unit
def test_calculate_dimension_scores_alias_match(session, setup_test_data):
    """Test dimension score calculation with alias match"""
    service = DimensionMappingService(session)
    data = setup_test_data
    
    # Column with alias match
    biz_category_col = data['columns'][2]
    candidates = service.calculate_dimension_scores(biz_category_col)
    
    assert len(candidates) > 0
    # Should match business_category via alias
    top_candidate = next(
        (c for c in candidates if c['dimension_name'] == 'business_category'),
        None
    )
    assert top_candidate is not None
    assert top_candidate['confidence'] == 'high'


@pytest.mark.unit
def test_calculate_dimension_scores_with_values(session, setup_test_data):
    """Test dimension score calculation with value-based matching"""
    service = DimensionMappingService(session)
    data = setup_test_data
    
    # Prepare value data
    field_values = ["electronics", "books", "clothing"]
    dimension_values_map = {
        data['dimensions'][1].id: ["electronics", "books", "clothing", "toys"]
    }
    
    # Column for category
    category_col = data['columns'][3]  # "categry" - typo
    candidates = service.calculate_dimension_scores(
        category_col,
        field_values=field_values,
        dimension_values_map=dimension_values_map
    )
    
    assert len(candidates) > 0
    # Should have category as a strong candidate due to value match
    category_candidate = next(
        (c for c in candidates if c['dimension_name'] == 'category'),
        None
    )
    assert category_candidate is not None
    assert category_candidate['scores']['value_match'] > 0.6


@pytest.mark.unit
def test_suggest_dimension_mappings(session, setup_test_data):
    """Test suggesting dimension mappings for a table"""
    service = DimensionMappingService(session)
    data = setup_test_data
    
    suggestions = service.suggest_dimension_mappings(
        table_id=data['table'].id,
        max_candidates=3
    )
    
    assert len(suggestions) > 0
    
    # Check that suggestions contain expected structure
    for column_id, suggestion in suggestions.items():
        assert 'column_id' in suggestion
        assert 'field_name' in suggestion
        assert 'candidates' in suggestion
        assert len(suggestion['candidates']) <= 3
        
        # Each candidate should have required fields
        for candidate in suggestion['candidates']:
            assert 'dimension_id' in candidate
            assert 'dimension_name' in candidate
            assert 'total_score' in candidate
            assert 'confidence' in candidate


@pytest.mark.unit
def test_apply_dimension_mapping(session, setup_test_data):
    """Test applying a dimension mapping"""
    service = DimensionMappingService(session)
    data = setup_test_data
    
    column = data['columns'][0]
    dimension = data['dimensions'][0]
    
    # Apply mapping
    success = service.apply_dimension_mapping(
        column_id=column.id,
        dimension_id=dimension.id,
        updated_by="test_user"
    )
    
    assert success is True
    
    # Verify mapping was applied
    session.refresh(column)
    assert column.dimension_id == dimension.id
    assert column.updated_by == "test_user"


@pytest.mark.unit
def test_apply_dimension_mapping_invalid_column(session, setup_test_data):
    """Test applying mapping with invalid column"""
    service = DimensionMappingService(session)
    data = setup_test_data
    
    success = service.apply_dimension_mapping(
        column_id=99999,
        dimension_id=data['dimensions'][0].id,
        updated_by="test_user"
    )
    
    assert success is False


@pytest.mark.unit
def test_apply_dimension_mapping_invalid_dimension(session, setup_test_data):
    """Test applying mapping with invalid dimension"""
    service = DimensionMappingService(session)
    data = setup_test_data
    
    success = service.apply_dimension_mapping(
        column_id=data['columns'][0].id,
        dimension_id=99999,
        updated_by="test_user"
    )
    
    assert success is False


@pytest.mark.unit
def test_confidence_calculation(session):
    """Test confidence level calculation"""
    service = DimensionMappingService(session)
    
    # High confidence - exact match
    scores = {
        'exact_match': 1.0,
        'alias_match': 0.0,
        'fuzzy_match': 0.0,
        'value_match': 0.0,
        'semantic_match': 0.0
    }
    confidence = service._calculate_confidence(1.0, scores)
    assert confidence == 'high'
    
    # High confidence - high value match
    scores = {
        'exact_match': 0.0,
        'alias_match': 0.0,
        'fuzzy_match': 0.0,
        'value_match': 0.85,
        'semantic_match': 0.3
    }
    confidence = service._calculate_confidence(1.0, scores)
    assert confidence == 'high'
    
    # Medium confidence - fuzzy + semantic
    scores = {
        'exact_match': 0.0,
        'alias_match': 0.0,
        'fuzzy_match': 0.8,
        'value_match': 0.0,
        'semantic_match': 0.3
    }
    confidence = service._calculate_confidence(0.7, scores)
    assert confidence == 'medium'
    
    # Low confidence
    scores = {
        'exact_match': 0.0,
        'alias_match': 0.0,
        'fuzzy_match': 0.5,
        'value_match': 0.0,
        'semantic_match': 0.0
    }
    confidence = service._calculate_confidence(0.4, scores)
    assert confidence == 'low'
