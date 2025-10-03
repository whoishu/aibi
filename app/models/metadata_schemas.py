"""Request and response schemas for metadata API endpoints"""

import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Base schemas for common fields
class MetadataBase(BaseModel):
    """Base schema for metadata with common fields"""
    gmt_create: Optional[datetime.datetime] = None
    gmt_modified: Optional[datetime.datetime] = None
    created_by: str
    updated_by: str
    status: int = 1


# Dimension schemas
class DimensionCreate(BaseModel):
    """Schema for creating a dimension"""
    name: str = Field(..., max_length=255, description="维度名称")
    verbose_name: str = Field(..., max_length=255, description="维度名称（中文）")
    alias: Optional[str] = Field(None, max_length=500, description="别名列表, 逗号分隔")
    parent_id: Optional[int] = Field(None, description="父维度ID")
    status: int = Field(1, description="状态, 1: 正常, 0: 下架")
    sensitive_level: Optional[int] = Field(None, description="敏感级别")
    data_type: str = Field("str", max_length=100, description="维度数据类型 varchar、array")
    dim_type: str = Field("dim", max_length=100, description="维度类型：dim/attr/ds")
    semantic_type: str = Field(..., max_length=20, description="语义类型DATE, ID, CATEGORY")
    description: Optional[str] = Field(None, max_length=1024)
    type_params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="类型参数")
    default_values: Optional[str] = Field(None, max_length=500, description="默认值")
    is_tag: Optional[bool] = Field(None, description="是否标签维度")
    expr: Dict[str, Any] = Field(default_factory=dict, description="表达式")
    ext: Optional[Dict[str, Any]] = Field(default_factory=dict, description="扩展信息")
    created_by: str = Field(..., max_length=100, description="创建人")
    updated_by: str = Field(..., max_length=100, description="更新人")
    original_id: Optional[int] = Field(None, description="从天机阁导入的维度原始ID")
    source: Optional[str] = Field("", max_length=100, description="维度来源，tjg/manual")
    entity_id: Optional[int] = Field(None, description="实体维度ID")


class DimensionUpdate(BaseModel):
    """Schema for updating a dimension"""
    name: Optional[str] = Field(None, max_length=255, description="维度名称")
    verbose_name: Optional[str] = Field(None, max_length=255, description="维度名称（中文）")
    alias: Optional[str] = Field(None, max_length=500, description="别名列表, 逗号分隔")
    parent_id: Optional[int] = Field(None, description="父维度ID")
    status: Optional[int] = Field(None, description="状态, 1: 正常, 0: 下架")
    sensitive_level: Optional[int] = Field(None, description="敏感级别")
    data_type: Optional[str] = Field(None, max_length=100, description="维度数据类型 varchar、array")
    dim_type: Optional[str] = Field(None, max_length=100, description="维度类型：dim/attr/ds")
    semantic_type: Optional[str] = Field(None, max_length=20, description="语义类型DATE, ID, CATEGORY")
    description: Optional[str] = Field(None, max_length=1024)
    type_params: Optional[Dict[str, Any]] = Field(None, description="类型参数")
    default_values: Optional[str] = Field(None, max_length=500, description="默认值")
    is_tag: Optional[bool] = Field(None, description="是否标签维度")
    expr: Optional[Dict[str, Any]] = Field(None, description="表达式")
    ext: Optional[Dict[str, Any]] = Field(None, description="扩展信息")
    updated_by: str = Field(..., max_length=100, description="更新人")
    original_id: Optional[int] = Field(None, description="从天机阁导入的维度原始ID")
    source: Optional[str] = Field(None, max_length=100, description="维度来源，tjg/manual")
    entity_id: Optional[int] = Field(None, description="实体维度ID")


class DimensionResponse(BaseModel):
    """Schema for dimension response"""
    id: int
    name: str
    verbose_name: str
    alias: Optional[str] = None
    parent_id: Optional[int] = None
    status: int
    sensitive_level: Optional[int] = None
    data_type: str
    dim_type: str
    semantic_type: str
    description: Optional[str] = None
    type_params: Optional[Dict[str, Any]] = None
    default_values: Optional[str] = None
    is_tag: Optional[bool] = None
    expr: Dict[str, Any]
    ext: Optional[Dict[str, Any]] = None
    gmt_create: Optional[datetime.datetime] = None
    gmt_modified: Optional[datetime.datetime] = None
    created_by: str
    updated_by: str
    original_id: Optional[int] = None
    source: Optional[str] = None
    entity_id: Optional[int] = None

    class Config:
        from_attributes = True


# Metric schemas
class MetricCreate(BaseModel):
    """Schema for creating a metric"""
    name: str = Field(..., max_length=100, description="指标名称")
    verbose_name: str = Field(..., max_length=100, description="指标名称（中文）")
    alias: Optional[str] = Field(None, max_length=500, description="别名列表, 逗号分隔")
    status: int = Field(1, description="状态, 1: 正常, 0: 下架")
    sensitive_level: Optional[int] = Field(None, description="敏感级别")
    data_type: str = Field("float", max_length=100, description="指标数据类型 varchar、array")
    data_type_params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="数据类型参数")
    data_format_type: Optional[str] = Field(None, max_length=50, description="数值类型")
    data_format: Optional[str] = Field(None, max_length=500, description="数值类型参数")
    related_dimensions: Optional[str] = Field(None, max_length=500, description="指标相关维度")
    related_tags: Optional[str] = Field(None, max_length=500, description="指标相关标签")
    description: Optional[str] = Field(None, max_length=2048)
    expression: Optional[str] = Field(None, max_length=1024, description="表达式")
    agg_type: Optional[str] = Field(None, max_length=100, description="聚合方式")
    unit: Optional[str] = Field(None, max_length=100, description="单位")
    is_created: bool = Field(False, description="是否创建，0：预定义，1：自动创建的")
    ext: Optional[Dict[str, Any]] = Field(default_factory=dict, description="扩展信息")
    created_by: str = Field(..., max_length=100, description="创建人")
    updated_by: str = Field(..., max_length=100, description="更新人")
    is_measure: Optional[bool] = Field(False, description="是否是度量")
    entity_id: Optional[int] = Field(None, description="实体ID")


class MetricUpdate(BaseModel):
    """Schema for updating a metric"""
    name: Optional[str] = Field(None, max_length=100, description="指标名称")
    verbose_name: Optional[str] = Field(None, max_length=100, description="指标名称（中文）")
    alias: Optional[str] = Field(None, max_length=500, description="别名列表, 逗号分隔")
    status: Optional[int] = Field(None, description="状态, 1: 正常, 0: 下架")
    sensitive_level: Optional[int] = Field(None, description="敏感级别")
    data_type: Optional[str] = Field(None, max_length=100, description="指标数据类型 varchar、array")
    data_type_params: Optional[Dict[str, Any]] = Field(None, description="数据类型参数")
    data_format_type: Optional[str] = Field(None, max_length=50, description="数值类型")
    data_format: Optional[str] = Field(None, max_length=500, description="数值类型参数")
    related_dimensions: Optional[str] = Field(None, max_length=500, description="指标相关维度")
    related_tags: Optional[str] = Field(None, max_length=500, description="指标相关标签")
    description: Optional[str] = Field(None, max_length=2048)
    expression: Optional[str] = Field(None, max_length=1024, description="表达式")
    agg_type: Optional[str] = Field(None, max_length=100, description="聚合方式")
    unit: Optional[str] = Field(None, max_length=100, description="单位")
    is_created: Optional[bool] = Field(None, description="是否创建，0：预定义，1：自动创建的")
    ext: Optional[Dict[str, Any]] = Field(None, description="扩展信息")
    updated_by: str = Field(..., max_length=100, description="更新人")
    is_measure: Optional[bool] = Field(None, description="是否是度量")
    entity_id: Optional[int] = Field(None, description="实体ID")


class MetricResponse(BaseModel):
    """Schema for metric response"""
    id: int
    name: str
    verbose_name: str
    alias: Optional[str] = None
    status: int
    sensitive_level: Optional[int] = None
    data_type: str
    data_type_params: Optional[Dict[str, Any]] = None
    data_format_type: Optional[str] = None
    data_format: Optional[str] = None
    related_dimensions: Optional[str] = None
    related_tags: Optional[str] = None
    description: Optional[str] = None
    expression: Optional[str] = None
    agg_type: Optional[str] = None
    unit: Optional[str] = None
    is_created: bool
    ext: Optional[Dict[str, Any]] = None
    gmt_create: Optional[datetime.datetime] = None
    gmt_modified: Optional[datetime.datetime] = None
    created_by: str
    updated_by: str
    is_measure: Optional[bool] = None
    entity_id: Optional[int] = None

    class Config:
        from_attributes = True


# Table schemas
class TableCreate(BaseModel):
    """Schema for creating a table"""
    name: str = Field(..., max_length=127, description="表名称")
    full_name: str = Field(..., max_length=127, description="全称，形式db.schema.table_name")
    verbose_name: str = Field(..., max_length=255, description="表名称（中文）")
    database_id: int = Field(..., description="数据库ID")
    domain_id: int = Field(..., description="默认主题域ID")
    db_name: Optional[str] = Field(None, max_length=100, description="数据库名称")
    schema_name: Optional[str] = Field(None, max_length=100, description="schema名称")
    description: Optional[str] = Field(None, max_length=2048, description="描述信息")
    domain_name: Optional[str] = Field(None, max_length=100, description="域")
    lifecycle: Optional[int] = Field(None, description="生命周期")
    latest_partition: Optional[str] = Field(None, max_length=100, description="最新分区")
    is_online_table: bool = Field(False, description="是否在线应用表， 0：不是， 1：是")
    table_type: Optional[str] = Field(None, max_length=100, description="表类型：fact/dim")
    created_by: str = Field(..., max_length=100, description="创建人")
    updated_by: str = Field(..., max_length=100, description="更新人")
    status: int = Field(1, description="状态, 1: 正常, 0: 下架")
    is_view: Optional[bool] = Field(False, description="是否视图表")
    sample_data: Optional[str] = Field(None, description="样例数据")
    ddl: Optional[str] = Field(None, description="表的DDL语句")
    weight: Optional[int] = Field(1, description="表的权重，影响搜索结果的排序，权重越高，越靠前")


class TableUpdate(BaseModel):
    """Schema for updating a table"""
    name: Optional[str] = Field(None, max_length=127, description="表名称")
    full_name: Optional[str] = Field(None, max_length=127, description="全称，形式db.schema.table_name")
    verbose_name: Optional[str] = Field(None, max_length=255, description="表名称（中文）")
    database_id: Optional[int] = Field(None, description="数据库ID")
    domain_id: Optional[int] = Field(None, description="默认主题域ID")
    db_name: Optional[str] = Field(None, max_length=100, description="数据库名称")
    schema_name: Optional[str] = Field(None, max_length=100, description="schema名称")
    description: Optional[str] = Field(None, max_length=2048, description="描述信息")
    domain_name: Optional[str] = Field(None, max_length=100, description="域")
    lifecycle: Optional[int] = Field(None, description="生命周期")
    latest_partition: Optional[str] = Field(None, max_length=100, description="最新分区")
    is_online_table: Optional[bool] = Field(None, description="是否在线应用表， 0：不是， 1：是")
    table_type: Optional[str] = Field(None, max_length=100, description="表类型：fact/dim")
    updated_by: str = Field(..., max_length=100, description="更新人")
    status: Optional[int] = Field(None, description="状态, 1: 正常, 0: 下架")
    is_view: Optional[bool] = Field(None, description="是否视图表")
    sample_data: Optional[str] = Field(None, description="样例数据")
    ddl: Optional[str] = Field(None, description="表的DDL语句")
    weight: Optional[int] = Field(None, description="表的权重，影响搜索结果的排序，权重越高，越靠前")


class TableResponse(BaseModel):
    """Schema for table response"""
    id: int
    name: str
    full_name: str
    verbose_name: str
    database_id: int
    domain_id: int
    db_name: Optional[str] = None
    schema_name: Optional[str] = None
    description: Optional[str] = None
    domain_name: Optional[str] = None
    lifecycle: Optional[int] = None
    latest_partition: Optional[str] = None
    is_online_table: bool
    table_type: Optional[str] = None
    gmt_create: Optional[datetime.datetime] = None
    gmt_modified: Optional[datetime.datetime] = None
    created_by: str
    updated_by: str
    status: int
    is_view: Optional[bool] = None
    sample_data: Optional[str] = None
    ddl: Optional[str] = None
    weight: Optional[int] = None

    class Config:
        from_attributes = True


# Entity schemas
class EntityCreate(BaseModel):
    """Schema for creating an entity"""
    entity_name: str = Field(..., max_length=255, description="实体名称")
    description: Optional[str] = Field(None, max_length=2048, description="描述")


class EntityUpdate(BaseModel):
    """Schema for updating an entity"""
    entity_name: Optional[str] = Field(None, max_length=255, description="实体名称")
    description: Optional[str] = Field(None, max_length=2048, description="描述")


class EntityResponse(BaseModel):
    """Schema for entity response"""
    id: int
    entity_name: str
    description: Optional[str] = None
    gmt_create: Optional[datetime.datetime] = None
    gmt_modified: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True


# Database schemas
class DatabaseCreate(BaseModel):
    """Schema for creating a database"""
    name: str = Field(..., max_length=255, description="数据库名称")
    db_type: str = Field(..., max_length=50, description="数据库类型")
    description: Optional[str] = Field(None, max_length=2048, description="描述")
    created_by: str = Field(..., max_length=100, description="创建人")
    updated_by: str = Field(..., max_length=100, description="更新人")
    status: int = Field(1, description="状态, 1: 正常, 0: 下架")


class DatabaseUpdate(BaseModel):
    """Schema for updating a database"""
    name: Optional[str] = Field(None, max_length=255, description="数据库名称")
    db_type: Optional[str] = Field(None, max_length=50, description="数据库类型")
    description: Optional[str] = Field(None, max_length=2048, description="描述")
    updated_by: str = Field(..., max_length=100, description="更新人")
    status: Optional[int] = Field(None, description="状态, 1: 正常, 0: 下架")


class DatabaseResponse(BaseModel):
    """Schema for database response"""
    id: int
    name: str
    db_type: str
    description: Optional[str] = None
    gmt_create: Optional[datetime.datetime] = None
    gmt_modified: Optional[datetime.datetime] = None
    created_by: str
    updated_by: str
    status: int

    class Config:
        from_attributes = True


# Domain schemas
class DomainCreate(BaseModel):
    """Schema for creating a domain"""
    name: str = Field(..., max_length=255, description="主题域名称")
    description: Optional[str] = Field(None, max_length=2048, description="描述")
    created_by: str = Field(..., max_length=100, description="创建人")
    updated_by: str = Field(..., max_length=100, description="更新人")
    status: int = Field(1, description="状态, 1: 正常, 0: 下架")


class DomainUpdate(BaseModel):
    """Schema for updating a domain"""
    name: Optional[str] = Field(None, max_length=255, description="主题域名称")
    description: Optional[str] = Field(None, max_length=2048, description="描述")
    updated_by: str = Field(..., max_length=100, description="更新人")
    status: Optional[int] = Field(None, description="状态, 1: 正常, 0: 下架")


class DomainResponse(BaseModel):
    """Schema for domain response"""
    id: int
    name: str
    description: Optional[str] = None
    gmt_create: Optional[datetime.datetime] = None
    gmt_modified: Optional[datetime.datetime] = None
    created_by: str
    updated_by: str
    status: int

    class Config:
        from_attributes = True


# List response schema
class ListResponse(BaseModel):
    """Generic list response schema"""
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(10, description="Page size")
