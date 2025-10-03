"""
Example script demonstrating automatic dimension mapping.

This example shows how to:
1. Create dimensions with aliases
2. Create a table with columns
3. Get dimension mapping suggestions
4. Apply dimension mappings
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/metadata"


def print_response(response, title):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print(f"Error: {response.text}")


def main():
    """Main example execution"""
    
    print("="*60)
    print("自动维度映射示例 (Automatic Dimension Mapping Example)")
    print("="*60)
    
    # 1. Create dimensions with aliases
    print("\n1. 创建测试维度...")
    
    dimensions = [
        {
            "name": "user_id",
            "verbose_name": "用户ID",
            "semantic_type": "ID",
            "alias": "uid,userId,user_identifier",
            "data_type": "bigint",
            "dim_type": "dim",
            "created_by": "admin",
            "updated_by": "admin",
            "status": 1
        },
        {
            "name": "business_category",
            "verbose_name": "业务类别",
            "semantic_type": "CATEGORY",
            "alias": "biz_category,biz_cat,business_cat",
            "data_type": "varchar",
            "dim_type": "dim",
            "created_by": "admin",
            "updated_by": "admin",
            "status": 1
        },
        {
            "name": "product_category",
            "verbose_name": "产品类别",
            "semantic_type": "CATEGORY",
            "alias": "category,cat,prod_category",
            "data_type": "varchar",
            "dim_type": "dim",
            "created_by": "admin",
            "updated_by": "admin",
            "status": 1
        },
        {
            "name": "created_date",
            "verbose_name": "创建日期",
            "semantic_type": "DATE",
            "alias": "create_date,creation_date",
            "data_type": "date",
            "dim_type": "dim",
            "created_by": "admin",
            "updated_by": "admin",
            "status": 1
        }
    ]
    
    dimension_ids = {}
    for dim_data in dimensions:
        response = requests.post(f"{BASE_URL}/dimensions", json=dim_data)
        if response.status_code == 201:
            dim_id = response.json()["id"]
            dimension_ids[dim_data["name"]] = dim_id
            print(f"  ✓ 创建维度: {dim_data['verbose_name']} (ID: {dim_id})")
        else:
            print(f"  ✗ 创建维度失败: {dim_data['name']}")
            print(f"    {response.text}")
    
    # 2. Create database and domain
    print("\n2. 创建数据库和主题域...")
    
    db_data = {
        "name": "sales_db",
        "db_type": "postgresql",
        "description": "销售数据库",
        "created_by": "admin",
        "updated_by": "admin",
        "status": 1
    }
    response = requests.post(f"{BASE_URL}/databases", json=db_data)
    if response.status_code == 201:
        database_id = response.json()["id"]
        print(f"  ✓ 创建数据库: sales_db (ID: {database_id})")
    else:
        print("  ✗ 创建数据库失败")
        return
    
    domain_data = {
        "name": "sales_domain",
        "description": "销售主题域",
        "created_by": "admin",
        "updated_by": "admin",
        "status": 1
    }
    response = requests.post(f"{BASE_URL}/domains", json=domain_data)
    if response.status_code == 201:
        domain_id = response.json()["id"]
        print(f"  ✓ 创建主题域: sales_domain (ID: {domain_id})")
    else:
        print("  ✗ 创建主题域失败")
        return
    
    # 3. Create a table
    print("\n3. 创建测试表...")
    
    table_data = {
        "name": "sales_orders",
        "full_name": "sales_db.public.sales_orders",
        "verbose_name": "销售订单表",
        "database_id": database_id,
        "domain_id": domain_id,
        "db_name": "sales_db",
        "schema_name": "public",
        "description": "存储销售订单信息",
        "table_type": "fact",
        "is_online_table": False,
        "is_view": False,
        "weight": 10,
        "created_by": "admin",
        "updated_by": "admin",
        "status": 1
    }
    response = requests.post(f"{BASE_URL}/tables", json=table_data)
    if response.status_code == 201:
        table_id = response.json()["id"]
        print(f"  ✓ 创建表: sales_orders (ID: {table_id})")
    else:
        print("  ✗ 创建表失败")
        print(f"    {response.text}")
        return
    
    # 4. Create table columns (normally these would be extracted from actual table schema)
    print("\n4. 创建表字段...")
    
    # Note: We need to create columns through the MetaTableColumn model
    # For this example, we'll simulate by directly creating them
    print("  注意: 在实际使用中，字段通常会在创建表时自动提取")
    print("  为了演示，我们假设表已经有以下字段:")
    print("    - userId (bigint)")
    print("    - biz_category (varchar)")
    print("    - categry (varchar) - 拼写错误")
    print("    - create_date (date)")
    print("    - order_amount (decimal)")
    
    # 5. Get dimension mapping suggestions
    print("\n5. 获取维度映射建议...")
    
    mapping_request = {
        "table_id": table_id,
        "max_candidates": 3,
        "min_score": 0.3
    }
    
    response = requests.post(
        f"{BASE_URL}/dimension-mapping/suggest",
        json=mapping_request
    )
    print_response(response, "维度映射建议")
    
    if response.status_code == 200:
        suggestions = response.json()
        
        # 6. Analyze and apply mappings
        print("\n6. 分析并应用映射...")
        
        for column_id, suggestion in suggestions.get("suggestions", {}).items():
            print(f"\n字段: {suggestion['field_name']} ({suggestion['logical_type']})")
            
            if suggestion['candidates']:
                print("候选维度:")
                for i, candidate in enumerate(suggestion['candidates'], 1):
                    print(f"  {i}. {candidate['dimension_verbose_name']} "
                          f"({candidate['dimension_name']})")
                    print(f"     - 总分: {candidate['total_score']:.2f}")
                    print(f"     - 置信度: {candidate['confidence']}")
                    print(f"     - 得分明细:")
                    for score_type, score_value in candidate['scores'].items():
                        if score_value > 0:
                            print(f"       • {score_type}: {score_value:.2f}")
                
                # Apply mapping if high confidence
                top_candidate = suggestion['candidates'][0]
                if top_candidate['confidence'] == 'high':
                    apply_request = {
                        "column_id": int(column_id),
                        "dimension_id": top_candidate['dimension_id'],
                        "updated_by": "admin"
                    }
                    
                    response = requests.post(
                        f"{BASE_URL}/dimension-mapping/apply",
                        json=apply_request
                    )
                    
                    if response.status_code == 200 and response.json()['success']:
                        print(f"\n  ✓ 自动应用映射: {top_candidate['dimension_verbose_name']}")
                    else:
                        print(f"\n  ✗ 应用映射失败: {response.text}")
                else:
                    print(f"\n  ⚠ 置信度不高，建议人工审核")
            else:
                print("  没有找到合适的候选维度")
    
    print("\n" + "="*60)
    print("示例完成！")
    print("="*60)
    print("\n提示:")
    print("1. 高置信度的映射会自动应用")
    print("2. 中低置信度的映射需要人工审核")
    print("3. 可以通过调整 min_score 参数来控制候选维度的数量")
    print("4. 为维度添加更多别名可以提高匹配准确度")


if __name__ == "__main__":
    print("="*60)
    print("自动维度映射 API 示例")
    print("="*60)
    print("\n确保服务器正在运行:")
    print("  python app/main.py")
    print("\n然后运行此示例:")
    print("  python examples/dimension_mapping_example.py")
    print("="*60)
    
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到服务器")
        print("请确保服务器运行在 http://localhost:8000")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
