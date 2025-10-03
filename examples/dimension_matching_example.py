"""Example demonstrating automatic dimension matching functionality"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import logging
from app.services.metadata_service import MetadataService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def setup_sample_data(service: MetadataService):
    """Create sample dimensions and table for demonstration"""
    logger.info("Setting up sample data...")
    
    # Create dimensions
    dimensions = [
        {
            "name": "username",
            "verbose_name": "用户名",
            "alias": "owner, user, creator",
            "semantic_type": "CATEGORY",
            "data_type": "varchar",
            "dim_type": "dim",
            "created_by": "demo",
            "updated_by": "demo",
        },
        {
            "name": "user_id",
            "verbose_name": "用户ID",
            "alias": "uid",
            "semantic_type": "ID",
            "data_type": "bigint",
            "dim_type": "dim",
            "created_by": "demo",
            "updated_by": "demo",
        },
        {
            "name": "category",
            "verbose_name": "分类",
            "alias": "biz_category, cat",
            "semantic_type": "CATEGORY",
            "data_type": "varchar",
            "dim_type": "dim",
            "created_by": "demo",
            "updated_by": "demo",
        },
        {
            "name": "create_time",
            "verbose_name": "创建时间",
            "alias": "created_at, created_date",
            "semantic_type": "DATE",
            "data_type": "datetime",
            "dim_type": "dim",
            "created_by": "demo",
            "updated_by": "demo",
        },
    ]
    
    created_dims = []
    for dim_data in dimensions:
        dim = service.create_dimension(dim_data)
        created_dims.append(dim)
        logger.info(f"Created dimension: {dim.name} (id={dim.id})")
    
    # Create database
    db = service.create_database({
        "name": "demo_db",
        "db_type": "mysql",
        "description": "Demo database",
        "created_by": "demo",
        "updated_by": "demo",
    })
    logger.info(f"Created database: {db.name} (id={db.id})")
    
    # Create domain
    domain = service.create_domain({
        "name": "demo_domain",
        "description": "Demo domain",
        "created_by": "demo",
        "updated_by": "demo",
    })
    logger.info(f"Created domain: {domain.name} (id={domain.id})")
    
    # Create table
    table = service.create_table({
        "name": "user_orders",
        "full_name": "demo_db.public.user_orders",
        "verbose_name": "用户订单表",
        "database_id": db.id,
        "domain_id": domain.id,
        "description": "包含用户订单信息的表",
        "created_by": "demo",
        "updated_by": "demo",
    })
    logger.info(f"Created table: {table.name} (id={table.id})")
    
    # Create columns with various naming styles
    from app.models.metadata import MetaTableColumn
    from sqlmodel import Session
    
    columns_data = [
        # Exact match
        ("username", "varchar(100)", "varchar", "用户名"),
        # Alias match
        ("owner", "varchar(100)", "varchar", "订单所有者"),
        # ID type with semantic filtering
        ("user_id", "bigint", "bigint", "用户ID"),
        # Fuzzy match (missing 'o')
        ("categry", "varchar(50)", "varchar", "分类"),
        # Date type
        ("created_at", "datetime", "datetime", "创建时间"),
        # No match (metric field)
        ("order_amount", "decimal(10,2)", "decimal", "订单金额"),
    ]
    
    with service._get_session() as session:
        for field_name, data_type, logical_type, desc in columns_data:
            col = MetaTableColumn(
                field_name=field_name,
                data_type=data_type,
                logical_type=logical_type,
                description=desc,
                table_id=table.id,
                created_by="demo",
                updated_by="demo",
            )
            session.add(col)
        session.commit()
    
    logger.info(f"Created {len(columns_data)} columns for table {table.name}")
    
    return table.id


def demonstrate_auto_matching():
    """Demonstrate automatic dimension matching"""
    print("\n" + "=" * 80)
    print("Automatic Dimension Matching Demo")
    print("=" * 80 + "\n")
    
    # Initialize service with in-memory database
    service = MetadataService(database_url="sqlite:///:memory:")
    
    # Setup sample data
    table_id = setup_sample_data(service)
    
    print("\n" + "-" * 80)
    print("Before Auto-Matching")
    print("-" * 80)
    
    # Show columns before matching
    columns = service.get_table_columns(table_id)
    for col in columns:
        dim_status = f"dimension_id={col.dimension_id}" if col.dimension_id else "No dimension"
        print(f"  {col.field_name:20s} ({col.logical_type:10s}) → {dim_status}")
    
    print("\n" + "-" * 80)
    print("Running Auto-Matching...")
    print("-" * 80 + "\n")
    
    # Perform auto-matching
    result = service.auto_match_table_dimensions(table_id, updated_by="demo")
    
    # Show results
    print(f"Total columns:    {result['total_columns']}")
    print(f"Matched columns:  {result['matched_columns']}")
    print(f"Unmatched:        {result['unmatched_columns']}")
    print(f"Updated:          {result['updated_columns']}")
    
    print("\n" + "-" * 80)
    print("After Auto-Matching")
    print("-" * 80)
    
    # Show columns after matching
    columns = service.get_table_columns(table_id)
    dimensions = {d.id: d for d in service.get_dimensions()}
    
    for col in columns:
        if col.dimension_id:
            dim = dimensions[col.dimension_id]
            match_info = f"dimension '{dim.name}' (id={dim.id})"
        else:
            match_info = "No match found"
        
        print(f"  {col.field_name:20s} ({col.logical_type:10s}) → {match_info}")
    
    print("\n" + "-" * 80)
    print("Matching Analysis")
    print("-" * 80)
    
    print("""
Expected matches:
  ✓ username   → dimension 'username' (exact match)
  ✓ owner      → dimension 'username' (alias match)
  ✓ user_id    → dimension 'user_id' (exact match + semantic type filtering)
  ✓ categry    → dimension 'category' (fuzzy match, distance=1)
  ✓ created_at → dimension 'create_time' (alias match)
  ✗ order_amount → No match (metric field, not a dimension)
    """)
    
    print("=" * 80)
    print("Demo completed!")
    print("=" * 80 + "\n")


def demonstrate_configuration():
    """Demonstrate custom configuration"""
    print("\n" + "=" * 80)
    print("Custom Configuration Demo")
    print("=" * 80 + "\n")
    
    from app.services.dimension_matcher_config import DimensionMatchConfig
    from app.services.dimension_matcher import DimensionMatcher
    
    print("Default Configuration:")
    print(f"  - Exact name match:        {DimensionMatchConfig.ENABLE_EXACT_NAME_MATCH}")
    print(f"  - Alias match:             {DimensionMatchConfig.ENABLE_ALIAS_MATCH}")
    print(f"  - Fuzzy match:             {DimensionMatchConfig.ENABLE_FUZZY_NAME_MATCH}")
    print(f"  - Fuzzy threshold:         {DimensionMatchConfig.FUZZY_MATCH_THRESHOLD}")
    print(f"  - Semantic type filtering: {DimensionMatchConfig.ENABLE_SEMANTIC_TYPE_FILTER}")
    print(f"  - Strict semantic type:    {DimensionMatchConfig.STRICT_SEMANTIC_TYPE}")
    
    print("\nSemantic Type Mappings:")
    for logical, semantic in DimensionMatchConfig.LOGICAL_TYPE_TO_SEMANTIC_TYPE.items():
        print(f"  {logical:15s} → {semantic}")
    
    print("\nCustom Configuration Example:")
    config = DimensionMatchConfig()
    config.FUZZY_MATCH_THRESHOLD = 1  # More strict
    config.STRICT_SEMANTIC_TYPE = True  # Require exact semantic type match
    
    print(f"  - Fuzzy threshold:      {config.FUZZY_MATCH_THRESHOLD} (more strict)")
    print(f"  - Strict semantic type: {config.STRICT_SEMANTIC_TYPE} (enabled)")
    
    matcher = DimensionMatcher(config)
    print("\nMatcher created with custom configuration!")


def main():
    """Main function"""
    try:
        demonstrate_auto_matching()
        demonstrate_configuration()
    except Exception as e:
        logger.error(f"Error in demo: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
