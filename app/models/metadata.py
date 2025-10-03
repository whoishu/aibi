"""Metadata models for database tables, dimensions, metrics, etc."""

import datetime
from typing import Any, Dict, List, Optional

from sqlmodel import Column, Field, JSON, Relationship, SQLModel


class IndexMixin:
    """Mixin for searchable tables"""
    __searchable__ = False


class MetaDatabase(SQLModel, table=True):
    """数据库信息"""
    
    __tablename__: str = "meta_database"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, unique=True, index=True, description="数据库名称")
    db_type: str = Field(max_length=50, description="数据库类型")
    description: Optional[str] = Field(default=None, max_length=2048, description="描述")
    gmt_create: Optional[datetime.datetime] = Field(default=None, description="创建时间")
    gmt_modified: Optional[datetime.datetime] = Field(default=None, description="更新时间")
    created_by: str = Field(max_length=100, description="创建人")
    updated_by: str = Field(max_length=100, description="更新人")
    status: int = Field(default=1, description="状态, 1: 正常, 0: 下架")
    
    # Relationships
    tables: List["MetaTable"] = Relationship(back_populates="database")


class MetaDomain(SQLModel, table=True):
    """主题域信息"""
    
    __tablename__: str = "meta_domain"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, unique=True, index=True, description="主题域名称")
    description: Optional[str] = Field(default=None, max_length=2048, description="描述")
    gmt_create: Optional[datetime.datetime] = Field(default=None, description="创建时间")
    gmt_modified: Optional[datetime.datetime] = Field(default=None, description="更新时间")
    created_by: str = Field(max_length=100, description="创建人")
    updated_by: str = Field(max_length=100, description="更新人")
    status: int = Field(default=1, description="状态, 1: 正常, 0: 下架")
    
    # Relationships
    tables: List["MetaTable"] = Relationship(back_populates="domain")


class MetaEntity(SQLModel, IndexMixin, table=True):
    """实体表"""

    __tablename__: str = "meta_entity"
    __searchable__ = True

    id: Optional[int] = Field(default=None, primary_key=True)
    entity_name: str = Field(max_length=255, description="实体名称")
    description: Optional[str] = Field(default=None, max_length=2048, description="描述")
    gmt_create: Optional[datetime.datetime] = Field(default=None, description="创建时间")
    gmt_modified: Optional[datetime.datetime] = Field(default=None, description="更新时间")

    # Relationships
    dimensions: List["MetaDimension"] = Relationship(back_populates="entity")
    metrics: List["MetaMetric"] = Relationship(back_populates="entity")


class MetaDimension(SQLModel, IndexMixin, table=True):
    """维度信息"""

    __tablename__: str = "meta_dimension"
    __searchable__ = True

    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    name: str = Field(max_length=255, unique=True, index=True, description="维度名称")
    verbose_name: str = Field(max_length=255, description="维度名称（中文）", index=True)
    alias: Optional[str] = Field(default=None, max_length=500, description="别名列表, 逗号分隔")
    parent_id: Optional[int] = Field(default=None, foreign_key="meta_dimension.id", description="父维度ID")
    status: int = Field(default=1, description="状态, 1: 正常, 0: 下架")
    sensitive_level: Optional[int] = Field(default=None, description="敏感级别")
    data_type: str = Field(default="str", max_length=100, description="维度数据类型 varchar、array")
    dim_type: str = Field(default="dim", max_length=100, description="维度类型：dim/attr/ds")
    semantic_type: str = Field(max_length=20, description="语义类型DATE, ID, CATEGORY")
    description: Optional[str] = Field(default=None, max_length=1024)
    type_params: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_column=Column(JSON), description="类型参数")
    default_values: Optional[str] = Field(default=None, max_length=500, description="默认值")
    is_tag: Optional[bool] = Field(default=None, description="是否标签维度")
    expr: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="表达式")
    ext: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_column=Column(JSON), description="扩展信息")
    gmt_create: Optional[datetime.datetime] = Field(default=None, description="创建时间")
    gmt_modified: Optional[datetime.datetime] = Field(default=None, description="更新时间")
    created_by: str = Field(max_length=100, description="创建人")
    updated_by: str = Field(max_length=100, description="更新人")
    original_id: Optional[int] = Field(default=None, description="从天机阁导入的维度原始ID")
    source: Optional[str] = Field(default="", max_length=100, description="维度来源，tjg/manual")
    entity_id: Optional[int] = Field(default=None, foreign_key="meta_entity.id", description="实体维度ID")

    # Relationships
    table_columns: List["MetaTableColumn"] = Relationship(back_populates="dimension")
    tags: List["MetaTag"] = Relationship(
        back_populates="dimension", sa_relationship_kwargs={"foreign_keys": "MetaTag.dimension_id"}
    )
    entity_tags: List["MetaTag"] = Relationship(
        back_populates="entity_dimension", sa_relationship_kwargs={"foreign_keys": "MetaTag.entity_dimension_id"}
    )
    entity: Optional["MetaEntity"] = Relationship(
        back_populates="dimensions", sa_relationship_kwargs={"foreign_keys": "MetaDimension.entity_id"}
    )


class MetaMetric(SQLModel, IndexMixin, table=True):
    """度量和指标"""

    __tablename__: str = "meta_metric"
    __searchable__ = True

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True, index=True, description="指标名称")
    verbose_name: str = Field(max_length=100, description="指标名称（中文）", index=True)
    alias: Optional[str] = Field(default=None, max_length=500, description="别名列表, 逗号分隔")
    status: int = Field(default=1, description="状态, 1: 正常, 0: 下架")
    sensitive_level: Optional[int] = Field(default=None, description="敏感级别")
    data_type: str = Field(default="float", max_length=100, description="指标数据类型 varchar、array")
    data_type_params: Optional[Dict[str, Any]] = Field(
        default_factory=dict, sa_column=Column(JSON), description="数据类型参数"
    )
    data_format_type: Optional[str] = Field(default=None, max_length=50, description="数值类型")
    data_format: Optional[str] = Field(default=None, max_length=500, description="数值类型参数")
    related_dimensions: Optional[str] = Field(default=None, max_length=500, description="指标相关维度")
    related_tags: Optional[str] = Field(default=None, max_length=500, description="指标相关标签")
    description: Optional[str] = Field(default=None, max_length=2048)
    expression: Optional[str] = Field(default=None, max_length=1024, description="表达式")
    agg_type: Optional[str] = Field(default=None, max_length=100, description="聚合方式")
    unit: Optional[str] = Field(default=None, max_length=100, description="单位")
    is_created: bool = Field(default=False, description="是否创建，0：预定义，1：自动创建的")
    ext: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_column=Column(JSON), description="扩展信息")
    gmt_create: Optional[datetime.datetime] = Field(default=None, description="创建时间")
    gmt_modified: Optional[datetime.datetime] = Field(default=None, description="更新时间")
    created_by: str = Field(max_length=100, description="创建人")
    updated_by: str = Field(max_length=100, description="更新人")
    is_measure: Optional[bool] = Field(default=False, description="是否是度量")
    entity_id: Optional[int] = Field(default=None, foreign_key="meta_entity.id", description="实体ID")

    # Relationships
    table_columns: List["MetaTableColumn"] = Relationship(back_populates="metric")
    tags: List["MetaTag"] = Relationship(back_populates="metric")
    entity: Optional["MetaEntity"] = Relationship(
        back_populates="metrics", sa_relationship_kwargs={"foreign_keys": "[MetaMetric.entity_id]"}
    )


class MetaTable(SQLModel, IndexMixin, table=True):
    """表信息"""

    __tablename__: str = "meta_table_info"
    __searchable__ = True

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=127, index=True, description="表名称")
    full_name: str = Field(max_length=127, description="全称，形式db.schema.table_name", index=True, unique=True)
    verbose_name: str = Field(max_length=255, description="表名称（中文）", index=True)
    database_id: int = Field(foreign_key="meta_database.id", description="数据库ID")
    domain_id: int = Field(foreign_key="meta_domain.id", description="默认主题域ID")
    db_name: Optional[str] = Field(default=None, max_length=100, description="数据库名称")
    schema_name: Optional[str] = Field(default=None, max_length=100, description="schema名称")
    description: Optional[str] = Field(default=None, max_length=2048, description="描述信息")
    domain_name: Optional[str] = Field(default=None, max_length=100, description="域")
    lifecycle: Optional[int] = Field(default=None, description="生命周期")
    latest_partition: Optional[str] = Field(default=None, max_length=100, description="最新分区")
    is_online_table: bool = Field(default=False, description="是否在线应用表， 0：不是， 1：是")
    table_type: Optional[str] = Field(default=None, max_length=100, description="表类型：fact/dim")
    gmt_create: Optional[datetime.datetime] = Field(default=None, description="创建时间")
    gmt_modified: Optional[datetime.datetime] = Field(default=None, description="更新时间")
    created_by: str = Field(max_length=100, description="创建人")
    updated_by: str = Field(max_length=100, description="更新人")
    status: int = Field(default=1, description="状态, 1: 正常, 0: 下架")
    is_view: Optional[bool] = Field(default=False, description="是否视图表")
    sample_data: Optional[str] = Field(default=None, description="样例数据")
    ddl: Optional[str] = Field(default=None, description="表的DDL语句")
    weight: Optional[int] = Field(default=1, description="表的权重，影响搜索结果的排序，权重越高，越靠前")

    # Relationships
    database: MetaDatabase = Relationship(back_populates="tables")
    domain: MetaDomain = Relationship(back_populates="tables")
    columns: List["MetaTableColumn"] = Relationship(back_populates="table")
    source_relations: List["MetaRelation"] = Relationship(
        back_populates="source_table", sa_relationship_kwargs={"foreign_keys": "MetaRelation.source_table_id"}
    )
    target_relations: List["MetaRelation"] = Relationship(
        back_populates="target_table", sa_relationship_kwargs={"foreign_keys": "MetaRelation.target_table_id"}
    )


class MetaTableColumn(SQLModel, IndexMixin, table=True):
    """表字段信息"""
    
    __tablename__: str = "meta_table_column"
    __searchable__ = True

    id: Optional[int] = Field(default=None, primary_key=True)
    field_name: str = Field(default="", max_length=100, description="字段名称", index=True)
    description: Optional[str] = Field(default=None, max_length=1024, description="描述")
    data_type: str = Field(max_length=100, description="数据表中实际的数据类型")
    logical_type: str = Field(max_length=100, description="逻辑数据类型")
    table_id: int = Field(foreign_key="meta_table_info.id", description="对应的表id", index=True)
    dimension_id: Optional[int] = Field(
        default=None, foreign_key="meta_dimension.id", description="对应的维度ID", index=True
    )
    metric_id: Optional[int] = Field(default=None, foreign_key="meta_metric.id", description="对应的指标", index=True)
    tag_id: Optional[int] = Field(default=None, description="该字段对应的tag")
    gmt_create: Optional[datetime.datetime] = Field(default=None, description="创建时间")
    gmt_modified: Optional[datetime.datetime] = Field(default=None, description="更新时间")
    created_by: str = Field(max_length=100, description="创建人")
    updated_by: str = Field(max_length=100, description="更新人")
    status: int = Field(default=1, description="状态, 1: 正常, 0: 下架")

    # Relationships
    table: MetaTable = Relationship(back_populates="columns")
    dimension: Optional[MetaDimension] = Relationship(back_populates="table_columns")
    metric: Optional[MetaMetric] = Relationship(back_populates="table_columns")


class MetaTag(SQLModel, table=True):
    """标签信息"""
    
    __tablename__: str = "meta_tag"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    tag_name: str = Field(max_length=255, description="标签名称", index=True)
    dimension_id: Optional[int] = Field(default=None, foreign_key="meta_dimension.id", description="维度ID")
    entity_dimension_id: Optional[int] = Field(default=None, foreign_key="meta_dimension.id", description="实体维度ID")
    metric_id: Optional[int] = Field(default=None, foreign_key="meta_metric.id", description="指标ID")
    description: Optional[str] = Field(default=None, max_length=2048, description="描述")
    gmt_create: Optional[datetime.datetime] = Field(default=None, description="创建时间")
    gmt_modified: Optional[datetime.datetime] = Field(default=None, description="更新时间")
    created_by: str = Field(max_length=100, description="创建人")
    updated_by: str = Field(max_length=100, description="更新人")
    status: int = Field(default=1, description="状态, 1: 正常, 0: 下架")
    
    # Relationships
    dimension: Optional[MetaDimension] = Relationship(
        back_populates="tags", sa_relationship_kwargs={"foreign_keys": "MetaTag.dimension_id"}
    )
    entity_dimension: Optional[MetaDimension] = Relationship(
        back_populates="entity_tags", sa_relationship_kwargs={"foreign_keys": "MetaTag.entity_dimension_id"}
    )
    metric: Optional[MetaMetric] = Relationship(back_populates="tags")


class MetaRelation(SQLModel, table=True):
    """表关系信息"""
    
    __tablename__: str = "meta_relation"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    source_table_id: int = Field(foreign_key="meta_table_info.id", description="源表ID", index=True)
    target_table_id: int = Field(foreign_key="meta_table_info.id", description="目标表ID", index=True)
    relation_type: str = Field(max_length=50, description="关系类型")
    description: Optional[str] = Field(default=None, max_length=2048, description="描述")
    gmt_create: Optional[datetime.datetime] = Field(default=None, description="创建时间")
    gmt_modified: Optional[datetime.datetime] = Field(default=None, description="更新时间")
    created_by: str = Field(max_length=100, description="创建人")
    updated_by: str = Field(max_length=100, description="更新人")
    status: int = Field(default=1, description="状态, 1: 正常, 0: 下架")
    
    # Relationships
    source_table: MetaTable = Relationship(
        back_populates="source_relations", sa_relationship_kwargs={"foreign_keys": "MetaRelation.source_table_id"}
    )
    target_table: MetaTable = Relationship(
        back_populates="target_relations", sa_relationship_kwargs={"foreign_keys": "MetaRelation.target_table_id"}
    )
