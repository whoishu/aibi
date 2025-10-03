"""Unit tests for metadata schemas"""

import pytest
from pydantic import ValidationError

from app.models.metadata_schemas import (
    DimensionCreate,
    DimensionUpdate,
    DimensionResponse,
    MetricCreate,
    MetricUpdate,
    MetricResponse,
    TableCreate,
    TableUpdate,
    TableResponse,
    EntityCreate,
    EntityUpdate,
    DatabaseCreate,
    DomainCreate,
)


@pytest.mark.unit
def test_dimension_create_valid():
    """Test valid dimension creation schema"""
    data = {
        "name": "user_id",
        "verbose_name": "用户ID",
        "semantic_type": "ID",
        "created_by": "test_user",
        "updated_by": "test_user"
    }
    
    dimension = DimensionCreate(**data)
    assert dimension.name == "user_id"
    assert dimension.verbose_name == "用户ID"
    assert dimension.semantic_type == "ID"
    assert dimension.status == 1
    assert dimension.data_type == "str"


@pytest.mark.unit
def test_dimension_create_with_all_fields():
    """Test dimension creation with all optional fields"""
    data = {
        "name": "product_category",
        "verbose_name": "产品类别",
        "alias": "category,类别",
        "semantic_type": "CATEGORY",
        "data_type": "varchar",
        "dim_type": "dim",
        "description": "产品分类维度",
        "type_params": {"max_length": 100},
        "expr": {"type": "field", "value": "category"},
        "ext": {"custom_field": "value"},
        "created_by": "admin",
        "updated_by": "admin",
        "source": "manual"
    }
    
    dimension = DimensionCreate(**data)
    assert dimension.name == "product_category"
    assert dimension.alias == "category,类别"
    assert dimension.type_params == {"max_length": 100}
    assert dimension.expr == {"type": "field", "value": "category"}


@pytest.mark.unit
def test_dimension_update_partial():
    """Test dimension update with partial fields"""
    data = {
        "verbose_name": "更新的名称",
        "updated_by": "admin"
    }
    
    dimension = DimensionUpdate(**data)
    assert dimension.verbose_name == "更新的名称"
    assert dimension.updated_by == "admin"
    assert dimension.name is None  # Not updated


@pytest.mark.unit
def test_metric_create_valid():
    """Test valid metric creation schema"""
    data = {
        "name": "revenue",
        "verbose_name": "销售额",
        "created_by": "test_user",
        "updated_by": "test_user"
    }
    
    metric = MetricCreate(**data)
    assert metric.name == "revenue"
    assert metric.verbose_name == "销售额"
    assert metric.data_type == "float"
    assert metric.status == 1


@pytest.mark.unit
def test_metric_create_with_optional_fields():
    """Test metric creation with optional fields"""
    data = {
        "name": "profit",
        "verbose_name": "利润",
        "alias": "profit,利润额",
        "data_type": "decimal",
        "data_type_params": {"precision": 10, "scale": 2},
        "description": "净利润指标",
        "expression": "revenue - cost",
        "agg_type": "sum",
        "unit": "元",
        "is_measure": True,
        "created_by": "admin",
        "updated_by": "admin"
    }
    
    metric = MetricCreate(**data)
    assert metric.name == "profit"
    assert metric.data_type == "decimal"
    assert metric.expression == "revenue - cost"
    assert metric.unit == "元"
    assert metric.is_measure is True


@pytest.mark.unit
def test_table_create_valid():
    """Test valid table creation schema"""
    data = {
        "name": "user_table",
        "full_name": "db.schema.user_table",
        "verbose_name": "用户表",
        "database_id": 1,
        "domain_id": 1,
        "created_by": "admin",
        "updated_by": "admin"
    }
    
    table = TableCreate(**data)
    assert table.name == "user_table"
    assert table.full_name == "db.schema.user_table"
    assert table.database_id == 1
    assert table.status == 1


@pytest.mark.unit
def test_table_create_with_optional_fields():
    """Test table creation with optional fields"""
    data = {
        "name": "sales_fact",
        "full_name": "dw.ods.sales_fact",
        "verbose_name": "销售事实表",
        "database_id": 1,
        "domain_id": 2,
        "db_name": "data_warehouse",
        "schema_name": "ods",
        "description": "销售明细事实表",
        "table_type": "fact",
        "is_view": False,
        "weight": 10,
        "created_by": "etl_user",
        "updated_by": "etl_user"
    }
    
    table = TableCreate(**data)
    assert table.name == "sales_fact"
    assert table.table_type == "fact"
    assert table.weight == 10


@pytest.mark.unit
def test_entity_create():
    """Test entity creation schema"""
    data = {
        "entity_name": "customer",
        "description": "客户实体"
    }
    
    entity = EntityCreate(**data)
    assert entity.entity_name == "customer"
    assert entity.description == "客户实体"


@pytest.mark.unit
def test_database_create():
    """Test database creation schema"""
    data = {
        "name": "production_db",
        "db_type": "postgresql",
        "description": "生产环境数据库",
        "created_by": "dba",
        "updated_by": "dba"
    }
    
    db = DatabaseCreate(**data)
    assert db.name == "production_db"
    assert db.db_type == "postgresql"
    assert db.status == 1


@pytest.mark.unit
def test_domain_create():
    """Test domain creation schema"""
    data = {
        "name": "sales_domain",
        "description": "销售主题域",
        "created_by": "admin",
        "updated_by": "admin"
    }
    
    domain = DomainCreate(**data)
    assert domain.name == "sales_domain"
    assert domain.description == "销售主题域"
    assert domain.status == 1


@pytest.mark.unit
def test_dimension_response():
    """Test dimension response schema can be created from dict"""
    data = {
        "id": 1,
        "name": "user_id",
        "verbose_name": "用户ID",
        "semantic_type": "ID",
        "data_type": "str",
        "dim_type": "dim",
        "expr": {},
        "status": 1,
        "created_by": "test_user",
        "updated_by": "test_user"
    }
    
    response = DimensionResponse(**data)
    assert response.id == 1
    assert response.name == "user_id"


@pytest.mark.unit
def test_metric_response():
    """Test metric response schema"""
    data = {
        "id": 1,
        "name": "revenue",
        "verbose_name": "销售额",
        "data_type": "float",
        "status": 1,
        "is_created": False,
        "created_by": "test_user",
        "updated_by": "test_user"
    }
    
    response = MetricResponse(**data)
    assert response.id == 1
    assert response.name == "revenue"


@pytest.mark.unit
def test_table_response():
    """Test table response schema"""
    data = {
        "id": 1,
        "name": "user_table",
        "full_name": "db.schema.user_table",
        "verbose_name": "用户表",
        "database_id": 1,
        "domain_id": 1,
        "is_online_table": False,
        "status": 1,
        "created_by": "admin",
        "updated_by": "admin"
    }
    
    response = TableResponse(**data)
    assert response.id == 1
    assert response.name == "user_table"


@pytest.mark.unit
def test_dimension_create_missing_required_field():
    """Test dimension creation fails with missing required field"""
    data = {
        "name": "test_dim",
        "verbose_name": "测试维度"
        # Missing semantic_type, created_by, updated_by
    }
    
    with pytest.raises(ValidationError) as exc_info:
        DimensionCreate(**data)
    
    errors = exc_info.value.errors()
    error_fields = [e['loc'][0] for e in errors]
    assert 'semantic_type' in error_fields
    assert 'created_by' in error_fields
    assert 'updated_by' in error_fields


@pytest.mark.unit
def test_metric_create_missing_required_field():
    """Test metric creation fails with missing required field"""
    data = {
        "name": "test_metric"
        # Missing verbose_name, created_by, updated_by
    }
    
    with pytest.raises(ValidationError) as exc_info:
        MetricCreate(**data)
    
    errors = exc_info.value.errors()
    error_fields = [e['loc'][0] for e in errors]
    assert 'verbose_name' in error_fields
    assert 'created_by' in error_fields


@pytest.mark.unit
def test_table_create_missing_required_fields():
    """Test table creation fails with missing required fields"""
    data = {
        "name": "test_table"
        # Missing full_name, verbose_name, database_id, domain_id, etc.
    }
    
    with pytest.raises(ValidationError) as exc_info:
        TableCreate(**data)
    
    errors = exc_info.value.errors()
    error_fields = [e['loc'][0] for e in errors]
    assert 'full_name' in error_fields
    assert 'database_id' in error_fields
