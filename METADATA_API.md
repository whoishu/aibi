# 元数据管理 API 文档

## 概述

元数据管理模块提供了完整的 CRUD（创建、读取、更新、删除）接口，支持管理数据库、主题域、表、字段、维度、指标等元数据信息。

## 基础URL

```
http://localhost:8000/api/v1/metadata
```

## 通用响应格式

### 成功响应
```json
{
  "id": 1,
  "name": "...",
  ...
}
```

### 列表响应
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 10
}
```

### 错误响应
```json
{
  "detail": "错误描述信息"
}
```

## API 端点

### 1. 维度管理（Dimensions）

#### 1.1 创建维度

**端点**: `POST /dimensions`

**请求体**:
```json
{
  "name": "user_id",
  "verbose_name": "用户ID",
  "semantic_type": "ID",
  "data_type": "str",
  "dim_type": "dim",
  "description": "用户唯一标识",
  "created_by": "admin",
  "updated_by": "admin",
  "status": 1
}
```

**响应** (201 Created):
```json
{
  "id": 1,
  "name": "user_id",
  "verbose_name": "用户ID",
  "semantic_type": "ID",
  "data_type": "str",
  "dim_type": "dim",
  "status": 1,
  "gmt_create": "2024-01-01T00:00:00",
  "gmt_modified": "2024-01-01T00:00:00",
  "created_by": "admin",
  "updated_by": "admin"
}
```

#### 1.2 获取维度详情

**端点**: `GET /dimensions/{dimension_id}`

**响应** (200 OK):
```json
{
  "id": 1,
  "name": "user_id",
  "verbose_name": "用户ID",
  "semantic_type": "ID",
  ...
}
```

#### 1.3 列出所有维度

**端点**: `GET /dimensions`

**查询参数**:
- `skip`: 跳过记录数 (默认: 0)
- `limit`: 每页记录数 (默认: 100, 最大: 1000)
- `status`: 状态过滤 (1=正常, 0=下架)

**示例**: `GET /dimensions?skip=0&limit=10&status=1`

**响应** (200 OK):
```json
{
  "items": [
    {
      "id": 1,
      "name": "user_id",
      "verbose_name": "用户ID",
      ...
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 10
}
```

#### 1.4 更新维度

**端点**: `PUT /dimensions/{dimension_id}`

**请求体** (只需要更新的字段):
```json
{
  "verbose_name": "更新的用户ID",
  "description": "更新的描述",
  "updated_by": "admin"
}
```

**响应** (200 OK):
```json
{
  "id": 1,
  "name": "user_id",
  "verbose_name": "更新的用户ID",
  "description": "更新的描述",
  ...
}
```

#### 1.5 删除维度（软删除）

**端点**: `DELETE /dimensions/{dimension_id}`

**响应** (204 No Content)

### 2. 指标管理（Metrics）

#### 2.1 创建指标

**端点**: `POST /metrics`

**请求体**:
```json
{
  "name": "revenue",
  "verbose_name": "销售额",
  "data_type": "float",
  "description": "总销售收入",
  "unit": "元",
  "agg_type": "sum",
  "created_by": "admin",
  "updated_by": "admin"
}
```

**响应** (201 Created):
```json
{
  "id": 1,
  "name": "revenue",
  "verbose_name": "销售额",
  "data_type": "float",
  "unit": "元",
  "agg_type": "sum",
  "status": 1,
  "is_created": false,
  "is_measure": false,
  ...
}
```

#### 2.2 获取指标详情

**端点**: `GET /metrics/{metric_id}`

#### 2.3 列出所有指标

**端点**: `GET /metrics`

**查询参数**: 同维度管理

#### 2.4 更新指标

**端点**: `PUT /metrics/{metric_id}`

#### 2.5 删除指标

**端点**: `DELETE /metrics/{metric_id}`

### 3. 表管理（Tables）

#### 3.1 创建表

**端点**: `POST /tables`

**请求体**:
```json
{
  "name": "user_table",
  "full_name": "db.schema.user_table",
  "verbose_name": "用户表",
  "database_id": 1,
  "domain_id": 1,
  "db_name": "production",
  "schema_name": "public",
  "description": "用户信息表",
  "table_type": "dim",
  "created_by": "admin",
  "updated_by": "admin"
}
```

**响应** (201 Created):
```json
{
  "id": 1,
  "name": "user_table",
  "full_name": "db.schema.user_table",
  "verbose_name": "用户表",
  "database_id": 1,
  "domain_id": 1,
  "table_type": "dim",
  "status": 1,
  "is_online_table": false,
  "is_view": false,
  "weight": 1,
  ...
}
```

#### 3.2 获取表详情

**端点**: `GET /tables/{table_id}`

#### 3.3 列出所有表

**端点**: `GET /tables`

**查询参数**: 同维度管理

#### 3.4 更新表

**端点**: `PUT /tables/{table_id}`

#### 3.5 删除表

**端点**: `DELETE /tables/{table_id}`

### 4. 实体管理（Entities）

#### 4.1 创建实体

**端点**: `POST /entities`

**请求体**:
```json
{
  "entity_name": "customer",
  "description": "客户实体"
}
```

**响应** (201 Created):
```json
{
  "id": 1,
  "entity_name": "customer",
  "description": "客户实体",
  "gmt_create": "2024-01-01T00:00:00",
  "gmt_modified": "2024-01-01T00:00:00"
}
```

#### 4.2 获取实体详情

**端点**: `GET /entities/{entity_id}`

#### 4.3 列出所有实体

**端点**: `GET /entities`

#### 4.4 更新实体

**端点**: `PUT /entities/{entity_id}`

#### 4.5 删除实体

**端点**: `DELETE /entities/{entity_id}`

### 5. 数据库管理（Databases）

#### 5.1 创建数据库

**端点**: `POST /databases`

**请求体**:
```json
{
  "name": "production_db",
  "db_type": "postgresql",
  "description": "生产环境数据库",
  "created_by": "dba",
  "updated_by": "dba",
  "status": 1
}
```

**响应** (201 Created):
```json
{
  "id": 1,
  "name": "production_db",
  "db_type": "postgresql",
  "description": "生产环境数据库",
  "status": 1,
  ...
}
```

#### 5.2 获取数据库详情

**端点**: `GET /databases/{database_id}`

#### 5.3 列出所有数据库

**端点**: `GET /databases`

#### 5.4 更新数据库

**端点**: `PUT /databases/{database_id}`

#### 5.5 删除数据库

**端点**: `DELETE /databases/{database_id}`

### 6. 主题域管理（Domains）

#### 6.1 创建主题域

**端点**: `POST /domains`

**请求体**:
```json
{
  "name": "sales_domain",
  "description": "销售主题域",
  "created_by": "admin",
  "updated_by": "admin",
  "status": 1
}
```

**响应** (201 Created):
```json
{
  "id": 1,
  "name": "sales_domain",
  "description": "销售主题域",
  "status": 1,
  ...
}
```

#### 6.2 获取主题域详情

**端点**: `GET /domains/{domain_id}`

#### 6.3 列出所有主题域

**端点**: `GET /domains`

#### 6.4 更新主题域

**端点**: `PUT /domains/{domain_id}`

#### 6.5 删除主题域

**端点**: `DELETE /domains/{domain_id}`

## 字段说明

### 维度（Dimension）字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 维度名称（英文） |
| verbose_name | string | 是 | 维度名称（中文） |
| semantic_type | string | 是 | 语义类型：DATE, ID, CATEGORY |
| data_type | string | 否 | 数据类型，默认 "str" |
| dim_type | string | 否 | 维度类型：dim/attr/ds，默认 "dim" |
| alias | string | 否 | 别名列表，逗号分隔 |
| parent_id | integer | 否 | 父维度ID |
| status | integer | 否 | 状态：1=正常，0=下架，默认 1 |
| sensitive_level | integer | 否 | 敏感级别 |
| description | string | 否 | 描述信息 |
| type_params | object | 否 | 类型参数 |
| default_values | string | 否 | 默认值 |
| is_tag | boolean | 否 | 是否标签维度 |
| expr | object | 否 | 表达式 |
| ext | object | 否 | 扩展信息 |
| entity_id | integer | 否 | 实体ID |
| source | string | 否 | 来源：tjg/manual |
| created_by | string | 是 | 创建人 |
| updated_by | string | 是 | 更新人 |

### 指标（Metric）字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 指标名称（英文） |
| verbose_name | string | 是 | 指标名称（中文） |
| data_type | string | 否 | 数据类型，默认 "float" |
| alias | string | 否 | 别名列表，逗号分隔 |
| status | integer | 否 | 状态：1=正常，0=下架 |
| sensitive_level | integer | 否 | 敏感级别 |
| data_type_params | object | 否 | 数据类型参数 |
| data_format_type | string | 否 | 数值类型 |
| data_format | string | 否 | 数值类型参数 |
| related_dimensions | string | 否 | 相关维度 |
| related_tags | string | 否 | 相关标签 |
| description | string | 否 | 描述信息 |
| expression | string | 否 | 计算表达式 |
| agg_type | string | 否 | 聚合方式：sum/avg/count等 |
| unit | string | 否 | 单位 |
| is_created | boolean | 否 | 是否自动创建 |
| is_measure | boolean | 否 | 是否度量 |
| ext | object | 否 | 扩展信息 |
| entity_id | integer | 否 | 实体ID |
| created_by | string | 是 | 创建人 |
| updated_by | string | 是 | 更新人 |

### 表（Table）字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 表名称 |
| full_name | string | 是 | 完整名称：db.schema.table |
| verbose_name | string | 是 | 表名称（中文） |
| database_id | integer | 是 | 数据库ID |
| domain_id | integer | 是 | 主题域ID |
| db_name | string | 否 | 数据库名 |
| schema_name | string | 否 | Schema名 |
| description | string | 否 | 描述信息 |
| domain_name | string | 否 | 域名 |
| lifecycle | integer | 否 | 生命周期（天） |
| latest_partition | string | 否 | 最新分区 |
| is_online_table | boolean | 否 | 是否在线表 |
| table_type | string | 否 | 表类型：fact/dim |
| status | integer | 否 | 状态：1=正常，0=下架 |
| is_view | boolean | 否 | 是否视图 |
| sample_data | string | 否 | 样例数据 |
| ddl | string | 否 | DDL语句 |
| weight | integer | 否 | 权重（影响搜索排序） |
| created_by | string | 是 | 创建人 |
| updated_by | string | 是 | 更新人 |

## 使用示例

### Python 示例

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/metadata"

# 创建维度
dimension_data = {
    "name": "user_id",
    "verbose_name": "用户ID",
    "semantic_type": "ID",
    "data_type": "str",
    "created_by": "admin",
    "updated_by": "admin"
}

response = requests.post(f"{BASE_URL}/dimensions", json=dimension_data)
dimension = response.json()
print(f"Created dimension with ID: {dimension['id']}")

# 获取维度列表
response = requests.get(f"{BASE_URL}/dimensions?skip=0&limit=10&status=1")
dimensions = response.json()
print(f"Total dimensions: {dimensions['total']}")

# 更新维度
update_data = {
    "verbose_name": "用户标识",
    "description": "唯一用户标识",
    "updated_by": "admin"
}
response = requests.put(f"{BASE_URL}/dimensions/{dimension['id']}", json=update_data)
updated = response.json()
print(f"Updated dimension: {updated['verbose_name']}")

# 删除维度（软删除）
response = requests.delete(f"{BASE_URL}/dimensions/{dimension['id']}")
print(f"Deleted dimension: {response.status_code == 204}")
```

### cURL 示例

```bash
# 创建维度
curl -X POST "http://localhost:8000/api/v1/metadata/dimensions" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "user_id",
    "verbose_name": "用户ID",
    "semantic_type": "ID",
    "created_by": "admin",
    "updated_by": "admin"
  }'

# 获取维度列表
curl "http://localhost:8000/api/v1/metadata/dimensions?skip=0&limit=10&status=1"

# 获取维度详情
curl "http://localhost:8000/api/v1/metadata/dimensions/1"

# 更新维度
curl -X PUT "http://localhost:8000/api/v1/metadata/dimensions/1" \
  -H "Content-Type: application/json" \
  -d '{
    "verbose_name": "用户标识",
    "updated_by": "admin"
  }'

# 删除维度
curl -X DELETE "http://localhost:8000/api/v1/metadata/dimensions/1"
```

## 错误码

| HTTP 状态码 | 说明 |
|------------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 删除成功（无内容） |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 503 | 服务未初始化 |

## 注意事项

1. 所有的删除操作都是软删除，只会将 `status` 设置为 0，不会真正删除数据
2. 分页参数 `skip` 和 `limit` 用于控制返回的数据量，避免一次性加载过多数据
3. 时间戳 `gmt_create` 和 `gmt_modified` 由系统自动管理，无需手动设置
4. 创建和更新操作需要提供 `created_by` 和 `updated_by` 字段，用于追踪操作人
5. 建议在实际使用中添加认证和权限控制机制

## 数据模型关系

```
Database (数据库)
  ├── Tables (表) [1:N]
  
Domain (主题域)
  ├── Tables (表) [1:N]
  
Entity (实体)
  ├── Dimensions (维度) [1:N]
  └── Metrics (指标) [1:N]
  
Table (表)
  ├── TableColumns (字段) [1:N]
  ├── source_relations (源关系) [1:N]
  └── target_relations (目标关系) [1:N]

Dimension (维度)
  ├── TableColumns (字段映射) [1:N]
  ├── Tags (标签) [1:N]
  └── Parent Dimension (父维度) [N:1]

Metric (指标)
  ├── TableColumns (字段映射) [1:N]
  └── Tags (标签) [1:N]
```
