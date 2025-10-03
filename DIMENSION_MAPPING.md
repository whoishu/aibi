# 自动维度映射 (Automatic Dimension Mapping)

## 概述

自动维度映射是一个智能系统，用于将数据表中的字段自动关联到已定义的维度。当新增数据表后，系统会分析表中的字段，并基于多种匹配策略推荐合适的维度候选项。

## 功能特性

### 匹配策略

系统综合使用以下多种匹配策略来识别字段对应的维度：

#### 1. 精确匹配 (Exact Match)
- **权重**: 1.0 (最高)
- **描述**: 字段名与维度名称完全一致（忽略大小写、下划线和驼峰命名差异）
- **示例**:
  - `user_id` → `user_id` ✓
  - `userId` → `user_id` ✓
  - `UserID` → `user_id` ✓

#### 2. 别名匹配 (Alias Match)
- **权重**: 0.95
- **描述**: 字段名在维度的别名列表中
- **示例**:
  - 维度 `user_id` 别名为 `uid,userId`
  - 字段 `uid` → `user_id` ✓

#### 3. 模糊匹配 (Fuzzy Match)
- **权重**: 0.5
- **描述**: 使用 Levenshtein 编辑距离算法处理拼写差异
- **阈值**: 相似度 ≥ 0.7
- **示例**:
  - `categry` → `category` ✓ (拼写错误)
  - `biz_cat` → `business_category` × (差异太大)

#### 4. 基于值的匹配 (Value-Based Match)
- **权重**: 1.2 (最高，当可用时)
- **描述**: 比较字段的唯一值与维度的可能取值
- **阈值**: 重叠率 ≥ 0.6
- **示例**:
  - 字段值: `["electronics", "books", "clothing"]`
  - 维度值: `["electronics", "books", "clothing", "toys"]`
  - 重叠率: 3/3 = 1.0 ✓

#### 5. 语义类型匹配 (Semantic Type Match)
- **权重**: 0.2 (辅助)
- **描述**: 检查字段的逻辑类型与维度的语义类型是否兼容
- **类型映射**:
  - `ID`: bigint, varchar, string, text
  - `DATE`: date, datetime, timestamp, time
  - `CATEGORY`: varchar, string, text, int, enum

### 评分系统

系统为每个候选维度计算加权总分：

```
总分 = (精确匹配分 × 1.0) + (别名匹配分 × 0.95) + (模糊匹配分 × 0.5) + 
       (值匹配分 × 1.2) + (语义匹配分 × 0.2)
```

### 置信度级别

- **高置信度 (High)**: 精确匹配、别名匹配或值匹配度 ≥ 0.8
- **中等置信度 (Medium)**: 模糊匹配 + 语义匹配，或值匹配度 ≥ 0.6
- **低置信度 (Low)**: 其他情况

## API 使用指南

### 1. 获取维度映射建议

**端点**: `POST /api/v1/metadata/dimension-mapping/suggest`

**请求体**:
```json
{
  "table_id": 123,
  "max_candidates": 5,
  "min_score": 0.3
}
```

**参数说明**:
- `table_id`: 要分析的表 ID
- `max_candidates`: 每个字段返回的最大候选数量（默认 5，范围 1-10）
- `min_score`: 最小分数阈值（默认 0.3，范围 0.0-1.0）

**响应示例**:
```json
{
  "table_id": 123,
  "suggestions": {
    "456": {
      "column_id": 456,
      "field_name": "user_id",
      "description": "用户标识",
      "logical_type": "bigint",
      "candidates": [
        {
          "dimension_id": 10,
          "dimension_name": "user_id",
          "dimension_verbose_name": "用户ID",
          "dimension_semantic_type": "ID",
          "total_score": 1.2,
          "scores": {
            "exact_match": 1.0,
            "alias_match": 0.0,
            "fuzzy_match": 0.0,
            "value_match": 0.0,
            "semantic_match": 0.2
          },
          "confidence": "high"
        },
        {
          "dimension_id": 11,
          "dimension_name": "customer_id",
          "dimension_verbose_name": "客户ID",
          "dimension_semantic_type": "ID",
          "total_score": 0.6,
          "scores": {
            "exact_match": 0.0,
            "alias_match": 0.0,
            "fuzzy_match": 0.4,
            "value_match": 0.0,
            "semantic_match": 0.2
          },
          "confidence": "low"
        }
      ]
    },
    "457": {
      "column_id": 457,
      "field_name": "biz_category",
      "description": "业务类别",
      "logical_type": "varchar",
      "candidates": [
        {
          "dimension_id": 20,
          "dimension_name": "business_category",
          "dimension_verbose_name": "业务类别",
          "dimension_semantic_type": "CATEGORY",
          "total_score": 1.15,
          "scores": {
            "exact_match": 0.0,
            "alias_match": 0.95,
            "fuzzy_match": 0.0,
            "value_match": 0.0,
            "semantic_match": 0.2
          },
          "confidence": "high"
        }
      ]
    }
  }
}
```

### 2. 应用维度映射

**端点**: `POST /api/v1/metadata/dimension-mapping/apply`

**请求体**:
```json
{
  "column_id": 456,
  "dimension_id": 10,
  "updated_by": "admin"
}
```

**参数说明**:
- `column_id`: 字段 ID
- `dimension_id`: 要映射的维度 ID
- `updated_by`: 执行操作的用户

**响应示例**:
```json
{
  "success": true,
  "message": "Successfully mapped column 456 to dimension 10"
}
```

## 使用场景

### 场景 1: 新增数据表后批量映射

```python
import requests

# 1. 获取表中所有字段的维度映射建议
response = requests.post(
    "http://localhost:8000/api/v1/metadata/dimension-mapping/suggest",
    json={
        "table_id": 123,
        "max_candidates": 5,
        "min_score": 0.5
    }
)

suggestions = response.json()

# 2. 遍历建议并展示给用户
for column_id, suggestion in suggestions["suggestions"].items():
    print(f"字段: {suggestion['field_name']}")
    print(f"候选维度:")
    for candidate in suggestion['candidates']:
        print(f"  - {candidate['dimension_verbose_name']} "
              f"(置信度: {candidate['confidence']}, "
              f"分数: {candidate['total_score']:.2f})")
    
    # 3. 自动应用高置信度的映射
    if suggestion['candidates'] and suggestion['candidates'][0]['confidence'] == 'high':
        apply_response = requests.post(
            "http://localhost:8000/api/v1/metadata/dimension-mapping/apply",
            json={
                "column_id": int(column_id),
                "dimension_id": suggestion['candidates'][0]['dimension_id'],
                "updated_by": "admin"
            }
        )
        print(f"  ✓ 自动应用映射: {apply_response.json()['message']}")
    else:
        print(f"  ⚠ 需要人工审核")
```

### 场景 2: 带值匹配的高精度映射

如果表已经有数据，可以提供字段的唯一值来提高匹配精度：

```python
# 从数据库采样字段唯一值
field_values = ["electronics", "books", "clothing", "toys"]

# 构建维度值映射
dimension_values_map = {
    20: ["electronics", "books", "clothing", "toys", "sports"],  # category 维度
    21: ["A", "B", "C"]  # 其他维度
}

# 在代码中使用（当前 API 暂不直接支持，可以通过扩展实现）
from app.services.dimension_mapping_service import DimensionMappingService
from sqlmodel import Session

with Session(engine) as session:
    mapping_service = DimensionMappingService(session)
    column = session.get(MetaTableColumn, column_id)
    
    candidates = mapping_service.calculate_dimension_scores(
        column=column,
        field_values=field_values,
        dimension_values_map=dimension_values_map
    )
```

## 性能优化建议

### 1. 维度值数量优化

- **问题**: 当维度唯一值数量超过 10 万时，值匹配可能影响性能
- **优化方案**:
  - 使用采样：`SELECT DISTINCT field_name FROM table LIMIT 1000`
  - 使用布隆过滤器进行快速成员检测
  - 缓存常用维度的唯一值集合

### 2. 批量处理

- 一次性处理整个表的所有字段，而不是逐个字段处理
- 预加载所有维度数据，减少数据库查询

### 3. 缓存策略

- 缓存维度列表和别名映射
- 缓存已计算的字段名标准化结果

## 工作流程

```
1. 用户新增数据表
   ↓
2. 系统自动分析未映射的字段
   ↓
3. 对每个字段计算所有候选维度的得分
   ├─ 精确匹配
   ├─ 别名匹配
   ├─ 模糊匹配
   ├─ 值匹配（如有数据）
   └─ 语义类型匹配
   ↓
4. 返回排序后的候选列表
   ↓
5. 用户审核并确认映射
   ├─ 高置信度：可自动应用
   └─ 中低置信度：需人工确认
   ↓
6. 应用映射，更新 dimension_id
```

## 扩展功能

### 未来优化方向

1. **机器学习增强**
   - 基于历史映射决策训练模型
   - 学习用户偏好和映射模式

2. **上下文感知**
   - 考虑表的主题域信息
   - 利用表间关系推断维度

3. **多语言支持**
   - 支持中英文混合字段名
   - 自动翻译和匹配

4. **维度值自动发现**
   - 自动从表中提取维度候选值
   - 建立维度值库

## 故障排查

### 常见问题

**Q: 为什么某个字段没有返回任何候选维度？**

A: 可能的原因：
- 字段的总分低于最小分数阈值（默认 0.3）
- 字段已经有维度映射（只处理未映射的字段）
- 所有维度都已下架（status=0）

**Q: 如何提高匹配精度？**

A: 建议：
- 为维度添加详细的别名列表
- 保持字段命名规范一致
- 提供维度的可能取值列表
- 降低 `min_score` 阈值查看更多候选

**Q: 模糊匹配不工作？**

A: 需要安装 `python-Levenshtein` 库：
```bash
pip install python-Levenshtein
```

## 相关文档

- [元数据管理 API](METADATA_API.md)
- [数据模型说明](app/models/metadata.py)
- [服务实现](app/services/dimension_mapping_service.py)
