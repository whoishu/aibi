# 自动维度映射功能实现总结

## 实现概述

本次实现完成了一个智能的字段-维度自动映射系统，用于将 `MetaTableColumn.dimension_id` 自动填充为正确的 `MetaDimension.id`。

## 核心功能

### 1. 多策略匹配系统

实现了以下五种匹配策略：

#### 精确匹配 (Exact Match)
- **权重**: 1.0
- **实现**: 字段名与维度名称完全一致（标准化后）
- **支持**: 大小写不敏感、驼峰命名转换、下划线处理
- **示例**: `user_id` ↔ `userId` ↔ `UserID`

#### 别名匹配 (Alias Match)
- **权重**: 0.95
- **实现**: 字段名在维度的别名列表中
- **支持**: 逗号分隔的别名列表
- **示例**: 字段 `uid` 匹配维度 `user_id` (别名: `uid,userId`)

#### 模糊匹配 (Fuzzy Match)
- **权重**: 0.5
- **实现**: Levenshtein 编辑距离算法
- **阈值**: 相似度 ≥ 0.7
- **依赖**: `python-Levenshtein` 库（可选）
- **示例**: `categry` ↔ `category` (拼写错误)

#### 值匹配 (Value-Based Match)
- **权重**: 1.2 (最高)
- **实现**: 比较字段唯一值与维度可能值的交集
- **阈值**: 重叠率 ≥ 0.6
- **适用**: 维度值数量适中的场景
- **优化**: 支持采样、缓存等性能优化

#### 语义类型匹配 (Semantic Type Match)
- **权重**: 0.2 (辅助)
- **实现**: 字段逻辑类型与维度语义类型的兼容性检查
- **类型映射**:
  - ID: bigint, varchar, string, text
  - DATE: date, datetime, timestamp, time
  - CATEGORY: varchar, string, text, int, enum

### 2. 智能评分系统

- **加权总分计算**: 
  ```
  总分 = Σ(策略得分 × 策略权重)
  ```
- **置信度评估**:
  - **高**: 精确/别名匹配或高值匹配 (≥0.8)
  - **中**: 模糊+语义匹配或中值匹配 (≥0.6)
  - **低**: 其他情况

### 3. 自动化工作流

```
新增数据表
    ↓
提取未映射字段
    ↓
计算候选维度得分
    ↓
返回排序候选列表
    ↓
用户审核/自动应用
    ↓
更新 dimension_id
```

## 技术实现

### 文件结构

```
app/
├── services/
│   └── dimension_mapping_service.py      # 核心服务实现
├── api/
│   └── metadata_routes.py                # API 端点（新增）
└── models/
    └── metadata_schemas.py               # 请求/响应模型（新增）

tests/
└── unit/
    └── test_dimension_mapping_service.py # 单元测试

examples/
└── dimension_mapping_example.py          # 使用示例

docs/
├── DIMENSION_MAPPING.md                  # 详细文档
└── METADATA_API.md                       # API 文档（更新）
```

### 核心类和方法

#### `DimensionMappingService`

**主要方法**:
- `calculate_dimension_scores()`: 计算单个字段的候选维度得分
- `suggest_dimension_mappings()`: 批量获取表中所有字段的映射建议
- `apply_dimension_mapping()`: 应用确认的维度映射

**辅助方法**:
- `_normalize_name()`: 标准化字段/维度名称
- `_exact_match_score()`: 精确匹配评分
- `_alias_match_score()`: 别名匹配评分
- `_fuzzy_match_score()`: 模糊匹配评分
- `_value_based_match_score()`: 值匹配评分
- `_semantic_type_match()`: 语义类型匹配
- `_calculate_confidence()`: 置信度计算

### API 端点

#### 1. 获取映射建议
- **端点**: `POST /api/v1/metadata/dimension-mapping/suggest`
- **功能**: 为表字段推荐候选维度
- **参数**:
  - `table_id`: 表 ID
  - `max_candidates`: 最大候选数（1-10，默认 5）
  - `min_score`: 最小分数阈值（0.0-1.0，默认 0.3）

#### 2. 应用映射
- **端点**: `POST /api/v1/metadata/dimension-mapping/apply`
- **功能**: 将维度映射应用到字段
- **参数**:
  - `column_id`: 字段 ID
  - `dimension_id`: 维度 ID
  - `updated_by`: 操作人

## 测试覆盖

### 单元测试（17 个测试用例）

1. **名称标准化测试**
   - 大小写转换
   - 驼峰命名转换
   - 下划线和连字符处理

2. **匹配策略测试**
   - 精确匹配：完全一致、大小写不敏感
   - 别名匹配：在别名列表中、不在列表中
   - 模糊匹配：高相似度、低相似度
   - 值匹配：高重叠、中重叠、低重叠
   - 语义匹配：兼容类型、不兼容类型

3. **评分系统测试**
   - 精确匹配场景
   - 别名匹配场景
   - 值匹配场景
   - 综合评分

4. **工作流测试**
   - 批量建议
   - 应用映射
   - 错误处理（无效字段、无效维度）

5. **置信度测试**
   - 高置信度场景
   - 中置信度场景
   - 低置信度场景

## 性能优化建议

### 1. 大数据量场景
- **问题**: 维度值超过 10 万时性能下降
- **方案**:
  - 采样查询：`SELECT DISTINCT field LIMIT 1000`
  - 布隆过滤器：快速成员检测
  - 缓存：常用维度值集合

### 2. 批量处理
- 一次性处理整表字段
- 预加载维度数据
- 减少数据库往返

### 3. 缓存策略
- 维度列表缓存
- 标准化名称缓存
- 计算结果缓存（TTL）

## 使用示例

### Python 代码

```python
import requests

# 1. 获取映射建议
response = requests.post(
    "http://localhost:8000/api/v1/metadata/dimension-mapping/suggest",
    json={
        "table_id": 123,
        "max_candidates": 5,
        "min_score": 0.3
    }
)

suggestions = response.json()

# 2. 自动应用高置信度映射
for column_id, suggestion in suggestions["suggestions"].items():
    candidates = suggestion['candidates']
    if candidates and candidates[0]['confidence'] == 'high':
        requests.post(
            "http://localhost:8000/api/v1/metadata/dimension-mapping/apply",
            json={
                "column_id": int(column_id),
                "dimension_id": candidates[0]['dimension_id'],
                "updated_by": "admin"
            }
        )
```

### cURL 示例

```bash
# 获取建议
curl -X POST "http://localhost:8000/api/v1/metadata/dimension-mapping/suggest" \
  -H "Content-Type: application/json" \
  -d '{"table_id": 123, "max_candidates": 5, "min_score": 0.3}'

# 应用映射
curl -X POST "http://localhost:8000/api/v1/metadata/dimension-mapping/apply" \
  -H "Content-Type: application/json" \
  -d '{"column_id": 456, "dimension_id": 10, "updated_by": "admin"}'
```

## 扩展性设计

### 当前支持
- ✅ 精确名称匹配
- ✅ 别名匹配
- ✅ 模糊匹配（Levenshtein）
- ✅ 值匹配（交集计算）
- ✅ 语义类型过滤
- ✅ 多策略加权评分
- ✅ 置信度评估

### 未来扩展方向
- 🔄 机器学习增强（基于历史决策训练）
- 🔄 上下文感知（表关系、主题域信息）
- 🔄 多语言支持（中英文混合识别）
- 🔄 维度值自动发现
- 🔄 时间衰减（历史映射权重降低）

## 依赖说明

### 必需依赖
- `sqlmodel`: 数据库 ORM
- `pydantic`: 数据验证和序列化
- `fastapi`: Web 框架

### 可选依赖
- `python-Levenshtein`: 模糊匹配（强烈推荐）
  ```bash
  pip install python-Levenshtein
  ```

## 配置建议

### 推荐参数
- **高精度场景**: `min_score=0.6`, `max_candidates=3`
- **高召回场景**: `min_score=0.3`, `max_candidates=5`
- **快速筛选**: `min_score=0.8`, `max_candidates=1`

### 维度设计建议
- 为每个维度添加详细的别名列表
- 保持字段命名规范一致
- 维护维度的可能取值列表
- 正确设置语义类型

## 监控指标

### 建议监控
1. **匹配成功率**: 高置信度建议被采纳的比例
2. **平均候选数**: 每个字段的平均候选维度数量
3. **处理时间**: 单表处理耗时
4. **用户修正率**: 用户修改建议的频率

## 总结

本实现提供了一个完整的、可扩展的维度自动映射系统，通过多种智能匹配策略和评分机制，能够准确地为表字段推荐合适的维度。系统支持批量处理、人工审核和自动应用，既能提高工作效率，又能保证映射质量。

### 主要优势
1. **智能匹配**: 多策略综合评分
2. **灵活配置**: 可调整阈值和候选数
3. **置信度评估**: 区分高中低置信度
4. **易于扩展**: 模块化设计，便于添加新策略
5. **性能优化**: 支持采样、缓存等优化手段
6. **完整文档**: 详细的 API 和使用文档

### 使用建议
1. 首次使用时，降低 `min_score` 查看更多候选
2. 为维度添加详尽的别名列表
3. 高置信度建议可以自动应用
4. 中低置信度建议需要人工审核
5. 定期分析用户反馈，优化匹配策略
