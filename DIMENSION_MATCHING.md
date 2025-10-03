# 表字段到维度的自动映射功能

## 概述

本功能实现了表字段到维度的智能自动映射，能够在新增数据表后，自动将表中的字段关联到已定义的维度（`meta_dimension`）。

## 功能特性

### 混合匹配策略

系统采用分层级的混合匹配策略，按以下顺序尝试匹配：

1. **精确名称匹配**（Exact Name Match）
   - 字段名与维度名称完全一致（不区分大小写）
   - 例如：`username` → 维度 `username`

2. **别名匹配**（Alias Match）
   - 字段名在维度的别名列表中
   - 例如：`owner` → 维度 `username`（假设 `username` 的别名包含 `owner`）

3. **语义类型过滤 + 模糊匹配**（Semantic Type Filtering + Fuzzy Match）
   - 根据字段的逻辑类型推断语义类型
   - 过滤出匹配语义类型的维度候选集
   - 使用 Levenshtein 距离进行模糊匹配
   - 例如：`categry` → 维度 `category`（编辑距离为 1）

### 语义类型推断

系统会根据字段的逻辑数据类型自动推断语义类型：

| 逻辑类型 | 语义类型 |
|---------|---------|
| bigint, int, integer, long | ID |
| varchar, string, text | CATEGORY |
| date, datetime, timestamp | DATE |
| 其他 | CATEGORY（默认） |

## 使用方法

### 基本使用

```python
from app.services.metadata_service import MetadataService

# 初始化服务
metadata_service = MetadataService()

# 对指定表的所有字段进行自动匹配
result = metadata_service.auto_match_table_dimensions(
    table_id=123,
    updated_by="admin"
)

# 查看匹配结果
print(f"总字段数: {result['total_columns']}")
print(f"匹配成功: {result['matched_columns']}")
print(f"未匹配: {result['unmatched_columns']}")
print(f"已更新: {result['updated_columns']}")
```

### 返回结果说明

`auto_match_table_dimensions()` 返回一个字典，包含以下信息：

- `total_columns`: 处理的字段总数
- `matched_columns`: 成功匹配到维度的字段数
- `unmatched_columns`: 未能匹配到维度的字段数
- `updated_columns`: 实际更新的字段数（跳过已有 dimension_id 的字段）

## 配置选项

### 默认配置

```python
from app.services.dimension_matcher_config import DimensionMatchConfig

# 名称匹配开关
DimensionMatchConfig.ENABLE_EXACT_NAME_MATCH = True  # 启用精确匹配
DimensionMatchConfig.ENABLE_ALIAS_MATCH = True  # 启用别名匹配
DimensionMatchConfig.ENABLE_FUZZY_NAME_MATCH = True  # 启用模糊匹配
DimensionMatchConfig.FUZZY_MATCH_THRESHOLD = 2  # 模糊匹配的编辑距离阈值

# 语义类型过滤
DimensionMatchConfig.ENABLE_SEMANTIC_TYPE_FILTER = True  # 启用语义类型过滤
DimensionMatchConfig.STRICT_SEMANTIC_TYPE = False  # 非严格模式
```

### 自定义配置

可以创建自定义配置实例：

```python
from app.services.dimension_matcher import DimensionMatcher
from app.services.dimension_matcher_config import DimensionMatchConfig

# 创建自定义配置
config = DimensionMatchConfig()
config.FUZZY_MATCH_THRESHOLD = 1  # 更严格的模糊匹配
config.STRICT_SEMANTIC_TYPE = True  # 严格要求语义类型一致

# 使用自定义配置
matcher = DimensionMatcher(config)
```

## 匹配示例

### 示例 1：精确匹配

**维度定义：**
- name: `username`
- verbose_name: `用户名`
- semantic_type: `CATEGORY`

**字段：**
- field_name: `username`
- logical_type: `varchar`

**结果：** ✅ 精确匹配成功

### 示例 2：别名匹配

**维度定义：**
- name: `username`
- alias: `owner, user, creator`
- semantic_type: `CATEGORY`

**字段：**
- field_name: `owner`
- logical_type: `varchar`

**结果：** ✅ 别名匹配成功

### 示例 3：模糊匹配

**维度定义：**
- name: `category`
- semantic_type: `CATEGORY`

**字段：**
- field_name: `categry` (缺少字母 'o')
- logical_type: `varchar`

**结果：** ✅ 模糊匹配成功（编辑距离为 1）

### 示例 4：语义类型过滤

**维度定义：**
- 维度 A: name: `user_id`, semantic_type: `ID`
- 维度 B: name: `username`, semantic_type: `CATEGORY`

**字段：**
- field_name: `userid` (与两个维度名称都相似)
- logical_type: `bigint`

**结果：** ✅ 匹配到维度 A (`user_id`)，因为语义类型过滤优先选择了 ID 类型

## API 集成示例

### FastAPI 端点示例

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class AutoMatchRequest(BaseModel):
    table_id: int

class AutoMatchResponse(BaseModel):
    total_columns: int
    matched_columns: int
    unmatched_columns: int
    updated_columns: int

@router.post("/api/v1/tables/{table_id}/auto-match-dimensions")
async def auto_match_dimensions(table_id: int) -> AutoMatchResponse:
    """自动匹配表字段到维度"""
    metadata_service = MetadataService()
    
    # 验证表是否存在
    table = metadata_service.get_table(table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    # 执行自动匹配
    result = metadata_service.auto_match_table_dimensions(
        table_id=table_id,
        updated_by="api_user"
    )
    
    return AutoMatchResponse(**result)
```

## 最佳实践

### 1. 维度别名设置

为常用的维度设置别名，提高匹配成功率：

```python
# 为 username 维度设置别名
dimension = metadata_service.update_dimension(
    dimension_id=1,
    data={
        "alias": "owner, user, creator, author"
    }
)
```

### 2. 语义类型一致性

确保维度的 semantic_type 设置准确：

```python
# ID 类型的维度
{
    "name": "user_id",
    "semantic_type": "ID",
    "data_type": "bigint"
}

# 分类类型的维度
{
    "name": "category",
    "semantic_type": "CATEGORY",
    "data_type": "varchar"
}
```

### 3. 批量处理

对多个表进行批量自动匹配：

```python
# 获取所有需要匹配的表
tables = metadata_service.get_tables(status=1)

# 批量处理
for table in tables:
    result = metadata_service.auto_match_table_dimensions(
        table_id=table.id,
        updated_by="batch_job"
    )
    print(f"Table {table.name}: {result['matched_columns']} matched")
```

### 4. 人工审核

对于关键表，建议先进行自动匹配，然后人工审核：

```python
# 执行自动匹配
result = metadata_service.auto_match_table_dimensions(table_id)

# 获取匹配结果
columns = metadata_service.get_table_columns(table_id)

# 显示匹配结果供人工审核
for col in columns:
    if col.dimension_id:
        dim = metadata_service.get_dimension(col.dimension_id)
        print(f"Column '{col.field_name}' → Dimension '{dim.name}'")
    else:
        print(f"Column '{col.field_name}' → No match (需要人工处理)")
```

## 局限性和注意事项

### 当前限制

1. **不支持基于值的匹配**：当前版本不支持通过采样字段值来匹配维度
2. **无 ML 模型支持**：尚未集成机器学习模型进行预测
3. **静态规则**：匹配规则是静态的，不会根据历史数据自动优化

### 注意事项

1. **已匹配字段不会重新匹配**：如果字段已经有 `dimension_id`，自动匹配会跳过该字段
2. **仅匹配活跃维度**：只会匹配 `status=1` 的维度
3. **编辑距离阈值**：默认编辑距离阈值为 2，太大可能导致错误匹配
4. **别名格式**：别名必须用逗号分隔，系统会自动去除空格

## 未来增强方向

### 阶段二：值匹配（2-4 周）

- 实现基于采样值的匹配
- 支持小规模枚举值的快速匹配
- 使用 Bloom Filter 优化大规模值匹配

### 阶段三：智能化（长期）

- 引入 MinHash/LSH 处理大规模唯一值
- 训练机器学习模型提高匹配准确率
- 支持用户反馈学习
- 提供匹配置信度评分

## 相关文档

- [元数据 API 文档](METADATA_API.md)
- [架构设计](ARCHITECTURE.md)
- [项目概述](README.md)

## 问题反馈

如有问题或建议，请在 GitHub Issues 中提交。
