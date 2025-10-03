"""Unit tests for metadata service"""

import pytest
from app.services.metadata_service import MetadataService
from app.models.metadata import MetaDimension, MetaMetric, MetaTable, MetaEntity


@pytest.fixture
def metadata_service():
    """Create a metadata service with in-memory database"""
    service = MetadataService(database_url="sqlite:///:memory:")
    return service


@pytest.mark.unit
def test_create_dimension(metadata_service):
    """Test creating a dimension through service"""
    data = {
        "name": "user_id",
        "verbose_name": "用户ID",
        "semantic_type": "ID",
        "data_type": "str",
        "dim_type": "dim",
        "created_by": "test_user",
        "updated_by": "test_user"
    }
    
    dimension = metadata_service.create_dimension(data)
    
    assert dimension.id is not None
    assert dimension.name == "user_id"
    assert dimension.verbose_name == "用户ID"
    assert dimension.gmt_create is not None
    assert dimension.gmt_modified is not None


@pytest.mark.unit
def test_get_dimension(metadata_service):
    """Test getting a dimension by ID"""
    data = {
        "name": "product_id",
        "verbose_name": "产品ID",
        "semantic_type": "ID",
        "created_by": "test_user",
        "updated_by": "test_user"
    }
    
    created = metadata_service.create_dimension(data)
    retrieved = metadata_service.get_dimension(created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == created.name


@pytest.mark.unit
def test_get_nonexistent_dimension(metadata_service):
    """Test getting a non-existent dimension"""
    result = metadata_service.get_dimension(99999)
    assert result is None


@pytest.mark.unit
def test_update_dimension(metadata_service):
    """Test updating a dimension"""
    data = {
        "name": "region",
        "verbose_name": "区域",
        "semantic_type": "CATEGORY",
        "created_by": "test_user",
        "updated_by": "test_user"
    }
    
    created = metadata_service.create_dimension(data)
    
    update_data = {
        "verbose_name": "地区",
        "description": "更新后的描述",
        "updated_by": "admin"
    }
    
    updated = metadata_service.update_dimension(created.id, update_data)
    
    assert updated is not None
    assert updated.verbose_name == "地区"
    assert updated.description == "更新后的描述"
    assert updated.updated_by == "admin"
    assert updated.gmt_modified > created.gmt_create


@pytest.mark.unit
def test_delete_dimension(metadata_service):
    """Test soft deleting a dimension"""
    data = {
        "name": "temp_dim",
        "verbose_name": "临时维度",
        "semantic_type": "CATEGORY",
        "created_by": "test_user",
        "updated_by": "test_user"
    }
    
    created = metadata_service.create_dimension(data)
    success = metadata_service.delete_dimension(created.id)
    
    assert success is True
    
    # Verify soft delete
    deleted = metadata_service.get_dimension(created.id)
    assert deleted.status == 0


@pytest.mark.unit
def test_get_all_dimensions(metadata_service):
    """Test getting all dimensions with pagination"""
    # Create multiple dimensions
    for i in range(5):
        data = {
            "name": f"dim_{i}",
            "verbose_name": f"维度{i}",
            "semantic_type": "CATEGORY",
            "created_by": "test_user",
            "updated_by": "test_user"
        }
        metadata_service.create_dimension(data)
    
    # Get first page
    dimensions = metadata_service.get_dimensions(skip=0, limit=3)
    assert len(dimensions) == 3
    
    # Get second page
    dimensions_page2 = metadata_service.get_dimensions(skip=3, limit=3)
    assert len(dimensions_page2) == 2


@pytest.mark.unit
def test_create_metric(metadata_service):
    """Test creating a metric through service"""
    data = {
        "name": "revenue",
        "verbose_name": "销售额",
        "data_type": "float",
        "created_by": "test_user",
        "updated_by": "test_user"
    }
    
    metric = metadata_service.create_metric(data)
    
    assert metric.id is not None
    assert metric.name == "revenue"
    assert metric.verbose_name == "销售额"
    assert metric.gmt_create is not None


@pytest.mark.unit
def test_get_metric(metadata_service):
    """Test getting a metric by ID"""
    data = {
        "name": "profit",
        "verbose_name": "利润",
        "data_type": "float",
        "created_by": "test_user",
        "updated_by": "test_user"
    }
    
    created = metadata_service.create_metric(data)
    retrieved = metadata_service.get_metric(created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == created.name


@pytest.mark.unit
def test_update_metric(metadata_service):
    """Test updating a metric"""
    data = {
        "name": "cost",
        "verbose_name": "成本",
        "data_type": "float",
        "created_by": "test_user",
        "updated_by": "test_user"
    }
    
    created = metadata_service.create_metric(data)
    
    update_data = {
        "verbose_name": "总成本",
        "unit": "元",
        "updated_by": "admin"
    }
    
    updated = metadata_service.update_metric(created.id, update_data)
    
    assert updated is not None
    assert updated.verbose_name == "总成本"
    assert updated.unit == "元"


@pytest.mark.unit
def test_create_entity(metadata_service):
    """Test creating an entity"""
    data = {
        "entity_name": "customer",
        "description": "客户实体"
    }
    
    entity = metadata_service.create_entity(data)
    
    assert entity.id is not None
    assert entity.entity_name == "customer"
    assert entity.description == "客户实体"


@pytest.mark.unit
def test_create_database(metadata_service):
    """Test creating a database"""
    data = {
        "name": "prod_db",
        "db_type": "postgresql",
        "description": "生产数据库",
        "created_by": "admin",
        "updated_by": "admin"
    }
    
    db = metadata_service.create_database(data)
    
    assert db.id is not None
    assert db.name == "prod_db"
    assert db.db_type == "postgresql"


@pytest.mark.unit
def test_create_domain(metadata_service):
    """Test creating a domain"""
    data = {
        "name": "sales_domain",
        "description": "销售主题域",
        "created_by": "admin",
        "updated_by": "admin"
    }
    
    domain = metadata_service.create_domain(data)
    
    assert domain.id is not None
    assert domain.name == "sales_domain"
    assert domain.description == "销售主题域"


@pytest.mark.unit
def test_count_dimensions(metadata_service):
    """Test counting dimensions"""
    # Create some dimensions
    for i in range(3):
        data = {
            "name": f"count_dim_{i}",
            "verbose_name": f"计数维度{i}",
            "semantic_type": "CATEGORY",
            "created_by": "test_user",
            "updated_by": "test_user"
        }
        metadata_service.create_dimension(data)
    
    count = metadata_service.count(MetaDimension)
    assert count >= 3


@pytest.mark.unit
def test_filter_by_status(metadata_service):
    """Test filtering dimensions by status"""
    # Create active dimension
    data1 = {
        "name": "active_dim",
        "verbose_name": "活跃维度",
        "semantic_type": "CATEGORY",
        "status": 1,
        "created_by": "test_user",
        "updated_by": "test_user"
    }
    metadata_service.create_dimension(data1)
    
    # Create inactive dimension
    data2 = {
        "name": "inactive_dim",
        "verbose_name": "非活跃维度",
        "semantic_type": "CATEGORY",
        "status": 0,
        "created_by": "test_user",
        "updated_by": "test_user"
    }
    metadata_service.create_dimension(data2)
    
    # Filter by status
    active_dims = metadata_service.get_dimensions(status=1)
    inactive_dims = metadata_service.get_dimensions(status=0)
    
    assert len(active_dims) >= 1
    assert len(inactive_dims) >= 1
    assert all(d.status == 1 for d in active_dims)
    assert all(d.status == 0 for d in inactive_dims)
