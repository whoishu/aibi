"""Unit tests for metadata models"""

import datetime
import pytest
from sqlmodel import Session, create_engine, SQLModel

from app.models.metadata import (
    MetaDatabase,
    MetaDimension,
    MetaDomain,
    MetaEntity,
    MetaMetric,
    MetaRelation,
    MetaTable,
    MetaTableColumn,
    MetaTag,
)


@pytest.fixture
def test_engine():
    """Create a test database engine"""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Create a test database session"""
    with Session(test_engine) as session:
        yield session


@pytest.mark.unit
def test_create_database(test_session):
    """Test creating a database record"""
    db = MetaDatabase(
        name="test_db",
        db_type="mysql",
        description="Test database",
        created_by="test_user",
        updated_by="test_user",
        status=1
    )
    test_session.add(db)
    test_session.commit()
    test_session.refresh(db)
    
    assert db.id is not None
    assert db.name == "test_db"
    assert db.db_type == "mysql"
    assert db.status == 1


@pytest.mark.unit
def test_create_domain(test_session):
    """Test creating a domain record"""
    domain = MetaDomain(
        name="test_domain",
        description="Test domain",
        created_by="test_user",
        updated_by="test_user",
        status=1
    )
    test_session.add(domain)
    test_session.commit()
    test_session.refresh(domain)
    
    assert domain.id is not None
    assert domain.name == "test_domain"
    assert domain.status == 1


@pytest.mark.unit
def test_create_entity(test_session):
    """Test creating an entity record"""
    entity = MetaEntity(
        entity_name="test_entity",
        description="Test entity"
    )
    test_session.add(entity)
    test_session.commit()
    test_session.refresh(entity)
    
    assert entity.id is not None
    assert entity.entity_name == "test_entity"


@pytest.mark.unit
def test_create_dimension(test_session):
    """Test creating a dimension record"""
    entity = MetaEntity(entity_name="user")
    test_session.add(entity)
    test_session.commit()
    test_session.refresh(entity)
    
    dimension = MetaDimension(
        name="user_id",
        verbose_name="用户ID",
        semantic_type="ID",
        data_type="str",
        dim_type="dim",
        created_by="test_user",
        updated_by="test_user",
        entity_id=entity.id
    )
    test_session.add(dimension)
    test_session.commit()
    test_session.refresh(dimension)
    
    assert dimension.id is not None
    assert dimension.name == "user_id"
    assert dimension.verbose_name == "用户ID"
    assert dimension.semantic_type == "ID"
    assert dimension.entity_id == entity.id


@pytest.mark.unit
def test_create_metric(test_session):
    """Test creating a metric record"""
    entity = MetaEntity(entity_name="sales")
    test_session.add(entity)
    test_session.commit()
    test_session.refresh(entity)
    
    metric = MetaMetric(
        name="revenue",
        verbose_name="销售额",
        data_type="float",
        created_by="test_user",
        updated_by="test_user",
        entity_id=entity.id
    )
    test_session.add(metric)
    test_session.commit()
    test_session.refresh(metric)
    
    assert metric.id is not None
    assert metric.name == "revenue"
    assert metric.verbose_name == "销售额"
    assert metric.data_type == "float"


@pytest.mark.unit
def test_create_table(test_session):
    """Test creating a table record"""
    db = MetaDatabase(
        name="test_db",
        db_type="mysql",
        created_by="test_user",
        updated_by="test_user"
    )
    test_session.add(db)
    test_session.commit()
    test_session.refresh(db)
    
    domain = MetaDomain(
        name="test_domain",
        created_by="test_user",
        updated_by="test_user"
    )
    test_session.add(domain)
    test_session.commit()
    test_session.refresh(domain)
    
    table = MetaTable(
        name="user_table",
        full_name="test_db.public.user_table",
        verbose_name="用户表",
        database_id=db.id,
        domain_id=domain.id,
        created_by="test_user",
        updated_by="test_user"
    )
    test_session.add(table)
    test_session.commit()
    test_session.refresh(table)
    
    assert table.id is not None
    assert table.name == "user_table"
    assert table.full_name == "test_db.public.user_table"
    assert table.database_id == db.id
    assert table.domain_id == domain.id


@pytest.mark.unit
def test_dimension_with_parent(test_session):
    """Test creating a dimension with parent"""
    parent_dim = MetaDimension(
        name="region",
        verbose_name="区域",
        semantic_type="CATEGORY",
        created_by="test_user",
        updated_by="test_user"
    )
    test_session.add(parent_dim)
    test_session.commit()
    test_session.refresh(parent_dim)
    
    child_dim = MetaDimension(
        name="city",
        verbose_name="城市",
        semantic_type="CATEGORY",
        parent_id=parent_dim.id,
        created_by="test_user",
        updated_by="test_user"
    )
    test_session.add(child_dim)
    test_session.commit()
    test_session.refresh(child_dim)
    
    assert child_dim.parent_id == parent_dim.id


@pytest.mark.unit
def test_dimension_default_values(test_session):
    """Test dimension default values"""
    dimension = MetaDimension(
        name="test_dim",
        verbose_name="测试维度",
        semantic_type="CATEGORY",
        created_by="test_user",
        updated_by="test_user"
    )
    test_session.add(dimension)
    test_session.commit()
    test_session.refresh(dimension)
    
    assert dimension.status == 1
    assert dimension.data_type == "str"
    assert dimension.dim_type == "dim"
    assert dimension.expr == {}
    assert dimension.type_params == {}


@pytest.mark.unit
def test_metric_default_values(test_session):
    """Test metric default values"""
    metric = MetaMetric(
        name="test_metric",
        verbose_name="测试指标",
        created_by="test_user",
        updated_by="test_user"
    )
    test_session.add(metric)
    test_session.commit()
    test_session.refresh(metric)
    
    assert metric.status == 1
    assert metric.data_type == "float"
    assert metric.is_created is False
    assert metric.is_measure is False
