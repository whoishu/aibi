"""Unit tests for metadata service"""

import pytest
from app.services.metadata_service import MetadataService
from app.models.metadata import MetaDimension, MetaMetric, MetaTable, MetaEntity, MetaTableColumn


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


@pytest.mark.unit
def test_auto_match_table_dimensions_exact_match(metadata_service):
    """Test auto-matching table dimensions with exact name match"""
    # Create dimensions
    dim1 = metadata_service.create_dimension({
        "name": "username",
        "verbose_name": "用户名",
        "semantic_type": "CATEGORY",
        "created_by": "test_user",
        "updated_by": "test_user"
    })
    
    dim2 = metadata_service.create_dimension({
        "name": "category",
        "verbose_name": "分类",
        "semantic_type": "CATEGORY",
        "created_by": "test_user",
        "updated_by": "test_user"
    })
    
    # Create database and domain
    db = metadata_service.create_database({
        "name": "test_db",
        "db_type": "mysql",
        "created_by": "test_user",
        "updated_by": "test_user"
    })
    
    domain = metadata_service.create_domain({
        "name": "test_domain",
        "created_by": "test_user",
        "updated_by": "test_user"
    })
    
    # Create table
    table = metadata_service.create_table({
        "name": "test_table",
        "full_name": "db.schema.test_table",
        "verbose_name": "测试表",
        "database_id": db.id,
        "domain_id": domain.id,
        "created_by": "test_user",
        "updated_by": "test_user"
    })
    
    # Create columns for the table
    from app.models.metadata import MetaTableColumn
    from sqlmodel import Session
    
    with metadata_service._get_session() as session:
        col1 = MetaTableColumn(
            field_name="username",
            data_type="varchar(100)",
            logical_type="varchar",
            table_id=table.id,
            created_by="test_user",
            updated_by="test_user"
        )
        col2 = MetaTableColumn(
            field_name="category",
            data_type="varchar(50)",
            logical_type="varchar",
            table_id=table.id,
            created_by="test_user",
            updated_by="test_user"
        )
        col3 = MetaTableColumn(
            field_name="count",
            data_type="int",
            logical_type="int",
            table_id=table.id,
            created_by="test_user",
            updated_by="test_user"
        )
        session.add(col1)
        session.add(col2)
        session.add(col3)
        session.commit()
        session.refresh(col1)
        session.refresh(col2)
        session.refresh(col3)
    
    # Run auto-matching
    result = metadata_service.auto_match_table_dimensions(table.id, updated_by="test_user")
    
    # Verify results
    assert result["total_columns"] == 3
    assert result["matched_columns"] == 2  # username and category
    assert result["unmatched_columns"] == 1  # count
    assert result["updated_columns"] == 2
    
    # Verify dimension_id was set correctly
    columns = metadata_service.get_table_columns(table.id)
    username_col = next(c for c in columns if c.field_name == "username")
    category_col = next(c for c in columns if c.field_name == "category")
    count_col = next(c for c in columns if c.field_name == "count")
    
    assert username_col.dimension_id == dim1.id
    assert category_col.dimension_id == dim2.id
    assert count_col.dimension_id is None


@pytest.mark.unit
def test_auto_match_table_dimensions_alias_match(metadata_service):
    """Test auto-matching with alias matching"""
    # Create dimension with aliases
    dim = metadata_service.create_dimension({
        "name": "username",
        "verbose_name": "用户名",
        "alias": "owner, user, creator",
        "semantic_type": "CATEGORY",
        "created_by": "test_user",
        "updated_by": "test_user"
    })
    
    # Create database and domain
    db = metadata_service.create_database({
        "name": "test_db2",
        "db_type": "mysql",
        "created_by": "test_user",
        "updated_by": "test_user"
    })
    
    domain = metadata_service.create_domain({
        "name": "test_domain2",
        "created_by": "test_user",
        "updated_by": "test_user"
    })
    
    # Create table
    table = metadata_service.create_table({
        "name": "test_table2",
        "full_name": "db.schema.test_table2",
        "verbose_name": "测试表2",
        "database_id": db.id,
        "domain_id": domain.id,
        "created_by": "test_user",
        "updated_by": "test_user"
    })
    
    # Create column with alias name
    from app.models.metadata import MetaTableColumn
    from sqlmodel import Session
    
    with metadata_service._get_session() as session:
        col = MetaTableColumn(
            field_name="owner",  # Matches alias
            data_type="varchar(100)",
            logical_type="varchar",
            table_id=table.id,
            created_by="test_user",
            updated_by="test_user"
        )
        session.add(col)
        session.commit()
        session.refresh(col)
    
    # Run auto-matching
    result = metadata_service.auto_match_table_dimensions(table.id, updated_by="test_user")
    
    # Verify alias match worked
    assert result["matched_columns"] == 1
    
    columns = metadata_service.get_table_columns(table.id)
    assert columns[0].dimension_id == dim.id


@pytest.mark.unit
def test_auto_match_table_dimensions_no_dimensions(metadata_service):
    """Test auto-matching when no dimensions exist"""
    # Create database and domain
    db = metadata_service.create_database({
        "name": "test_db3",
        "db_type": "mysql",
        "created_by": "test_user",
        "updated_by": "test_user"
    })
    
    domain = metadata_service.create_domain({
        "name": "test_domain3",
        "created_by": "test_user",
        "updated_by": "test_user"
    })
    
    # Create table
    table = metadata_service.create_table({
        "name": "test_table3",
        "full_name": "db.schema.test_table3",
        "verbose_name": "测试表3",
        "database_id": db.id,
        "domain_id": domain.id,
        "created_by": "test_user",
        "updated_by": "test_user"
    })
    
    # Create column
    from app.models.metadata import MetaTableColumn
    from sqlmodel import Session
    
    with metadata_service._get_session() as session:
        col = MetaTableColumn(
            field_name="some_field",
            data_type="varchar(100)",
            logical_type="varchar",
            table_id=table.id,
            created_by="test_user",
            updated_by="test_user"
        )
        session.add(col)
        session.commit()
    
    # Run auto-matching (no dimensions should exist at this point in fresh DB)
    result = metadata_service.auto_match_table_dimensions(table.id, updated_by="test_user")
    
    # Should handle gracefully
    assert result["total_columns"] == 1
    assert result["matched_columns"] == 0


@pytest.mark.unit
def test_get_table_columns(metadata_service):
    """Test getting table columns"""
    # Create database and domain
    db = metadata_service.create_database({
        "name": "test_db4",
        "db_type": "mysql",
        "created_by": "test_user",
        "updated_by": "test_user"
    })
    
    domain = metadata_service.create_domain({
        "name": "test_domain4",
        "created_by": "test_user",
        "updated_by": "test_user"
    })
    
    # Create table
    table = metadata_service.create_table({
        "name": "test_table4",
        "full_name": "db.schema.test_table4",
        "verbose_name": "测试表4",
        "database_id": db.id,
        "domain_id": domain.id,
        "created_by": "test_user",
        "updated_by": "test_user"
    })
    
    # Create columns
    from app.models.metadata import MetaTableColumn
    from sqlmodel import Session
    
    with metadata_service._get_session() as session:
        for i in range(3):
            col = MetaTableColumn(
                field_name=f"field_{i}",
                data_type="varchar(100)",
                logical_type="varchar",
                table_id=table.id,
                created_by="test_user",
                updated_by="test_user"
            )
            session.add(col)
        session.commit()
    
    # Get columns
    columns = metadata_service.get_table_columns(table.id)
    
    assert len(columns) == 3
    assert all(c.table_id == table.id for c in columns)
