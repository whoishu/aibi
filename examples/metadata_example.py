"""
Example script demonstrating metadata management API usage.

This example shows how to:
1. Create a database
2. Create a domain
3. Create dimensions
4. Create metrics
5. Create a table
6. Query and update metadata
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/metadata"


def print_response(response, title):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)


def main():
    """Main example execution"""
    
    # 1. Create a database
    print("\n1. Creating a database...")
    db_data = {
        "name": "sales_db",
        "db_type": "postgresql",
        "description": "销售数据库",
        "created_by": "admin",
        "updated_by": "admin",
        "status": 1
    }
    response = requests.post(f"{BASE_URL}/databases", json=db_data)
    print_response(response, "Create Database")
    database_id = response.json()["id"]
    
    # 2. Create a domain
    print("\n2. Creating a domain...")
    domain_data = {
        "name": "sales_domain",
        "description": "销售主题域",
        "created_by": "admin",
        "updated_by": "admin",
        "status": 1
    }
    response = requests.post(f"{BASE_URL}/domains", json=domain_data)
    print_response(response, "Create Domain")
    domain_id = response.json()["id"]
    
    # 3. Create an entity
    print("\n3. Creating an entity...")
    entity_data = {
        "entity_name": "customer",
        "description": "客户实体"
    }
    response = requests.post(f"{BASE_URL}/entities", json=entity_data)
    print_response(response, "Create Entity")
    entity_id = response.json()["id"]
    
    # 4. Create dimensions
    print("\n4. Creating dimensions...")
    dimensions = [
        {
            "name": "user_id",
            "verbose_name": "用户ID",
            "semantic_type": "ID",
            "data_type": "str",
            "dim_type": "dim",
            "description": "用户唯一标识",
            "created_by": "admin",
            "updated_by": "admin",
            "entity_id": entity_id
        },
        {
            "name": "region",
            "verbose_name": "地区",
            "semantic_type": "CATEGORY",
            "data_type": "str",
            "dim_type": "dim",
            "description": "销售地区",
            "created_by": "admin",
            "updated_by": "admin"
        },
        {
            "name": "order_date",
            "verbose_name": "订单日期",
            "semantic_type": "DATE",
            "data_type": "date",
            "dim_type": "ds",
            "description": "订单创建日期",
            "created_by": "admin",
            "updated_by": "admin"
        }
    ]
    
    dimension_ids = []
    for dim_data in dimensions:
        response = requests.post(f"{BASE_URL}/dimensions", json=dim_data)
        print_response(response, f"Create Dimension: {dim_data['name']}")
        dimension_ids.append(response.json()["id"])
    
    # 5. Create metrics
    print("\n5. Creating metrics...")
    metrics = [
        {
            "name": "revenue",
            "verbose_name": "销售额",
            "data_type": "float",
            "description": "总销售收入",
            "unit": "元",
            "agg_type": "sum",
            "expression": "price * quantity",
            "is_measure": False,
            "created_by": "admin",
            "updated_by": "admin",
            "entity_id": entity_id
        },
        {
            "name": "order_count",
            "verbose_name": "订单数",
            "data_type": "int",
            "description": "订单总数",
            "unit": "个",
            "agg_type": "count",
            "created_by": "admin",
            "updated_by": "admin"
        }
    ]
    
    metric_ids = []
    for metric_data in metrics:
        response = requests.post(f"{BASE_URL}/metrics", json=metric_data)
        print_response(response, f"Create Metric: {metric_data['name']}")
        metric_ids.append(response.json()["id"])
    
    # 6. Create a table
    print("\n6. Creating a table...")
    table_data = {
        "name": "sales_fact",
        "full_name": "sales_db.public.sales_fact",
        "verbose_name": "销售事实表",
        "database_id": database_id,
        "domain_id": domain_id,
        "db_name": "sales_db",
        "schema_name": "public",
        "description": "销售明细事实表",
        "table_type": "fact",
        "is_online_table": False,
        "is_view": False,
        "weight": 10,
        "created_by": "admin",
        "updated_by": "admin"
    }
    response = requests.post(f"{BASE_URL}/tables", json=table_data)
    print_response(response, "Create Table")
    table_id = response.json()["id"]
    
    # 7. List dimensions with pagination
    print("\n7. Listing all dimensions...")
    response = requests.get(f"{BASE_URL}/dimensions?skip=0&limit=10&status=1")
    print_response(response, "List Dimensions")
    
    # 8. Get a specific dimension
    print("\n8. Getting dimension details...")
    response = requests.get(f"{BASE_URL}/dimensions/{dimension_ids[0]}")
    print_response(response, f"Get Dimension ID: {dimension_ids[0]}")
    
    # 9. Update a dimension
    print("\n9. Updating dimension...")
    update_data = {
        "verbose_name": "客户ID（更新）",
        "description": "更新后的客户唯一标识",
        "updated_by": "admin"
    }
    response = requests.put(f"{BASE_URL}/dimensions/{dimension_ids[0]}", json=update_data)
    print_response(response, f"Update Dimension ID: {dimension_ids[0]}")
    
    # 10. List metrics
    print("\n10. Listing all metrics...")
    response = requests.get(f"{BASE_URL}/metrics?skip=0&limit=10")
    print_response(response, "List Metrics")
    
    # 11. Get table details
    print("\n11. Getting table details...")
    response = requests.get(f"{BASE_URL}/tables/{table_id}")
    print_response(response, f"Get Table ID: {table_id}")
    
    # 12. Update table weight
    print("\n12. Updating table weight...")
    update_data = {
        "weight": 20,
        "description": "更新后的销售事实表",
        "updated_by": "admin"
    }
    response = requests.put(f"{BASE_URL}/tables/{table_id}", json=update_data)
    print_response(response, f"Update Table ID: {table_id}")
    
    # 13. List entities
    print("\n13. Listing all entities...")
    response = requests.get(f"{BASE_URL}/entities")
    print_response(response, "List Entities")
    
    # 14. Demonstrate soft delete
    print("\n14. Soft deleting a metric...")
    response = requests.delete(f"{BASE_URL}/metrics/{metric_ids[1]}")
    print_response(response, f"Delete Metric ID: {metric_ids[1]}")
    
    # Verify soft delete - metric should still exist but with status=0
    response = requests.get(f"{BASE_URL}/metrics/{metric_ids[1]}")
    print_response(response, f"Verify Soft Delete - Get Metric ID: {metric_ids[1]}")
    
    print("\n" + "="*60)
    print("Example completed successfully!")
    print("="*60)


if __name__ == "__main__":
    print("="*60)
    print("Metadata Management API Example")
    print("="*60)
    print("\nMake sure the server is running:")
    print("  python app/main.py")
    print("\nThen run this example:")
    print("  python examples/metadata_example.py")
    print("="*60)
    
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Please make sure the server is running at http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
