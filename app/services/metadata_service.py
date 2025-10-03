"""Service for metadata management operations"""

import datetime
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlmodel import Session, create_engine, select

from app.models.metadata import (
    MetaDatabase,
    MetaDimension,
    MetaDimensionValue,
    MetaDomain,
    MetaEntity,
    MetaMetric,
    MetaTable,
    MetaTableColumn,
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class MetadataService:
    """Service for metadata CRUD operations"""

    def __init__(self, database_url: str = "sqlite:///./metadata.db"):
        """Initialize metadata service with database connection
        
        Args:
            database_url: Database connection URL
        """
        self.engine = create_engine(database_url, echo=False)
        self._create_tables()

    def _create_tables(self):
        """Create all metadata tables if they don't exist"""
        from sqlmodel import SQLModel
        from app.models.metadata import (
            MetaDatabase,
            MetaDimension,
            MetaDimensionValue,
            MetaDomain,
            MetaEntity,
            MetaMetric,
            MetaRelation,
            MetaTable,
            MetaTableColumn,
            MetaTag,
        )
        
        SQLModel.metadata.create_all(self.engine)
        logger.info("Metadata tables created successfully")

    def _get_session(self) -> Session:
        """Get a database session"""
        return Session(self.engine)

    def _update_timestamps(self, obj: Any, is_create: bool = False):
        """Update timestamp fields"""
        now = datetime.datetime.now()
        if is_create:
            obj.gmt_create = now
        obj.gmt_modified = now

    # Generic CRUD operations
    def create(self, model_class: Type[T], data: Dict[str, Any]) -> T:
        """Create a new record
        
        Args:
            model_class: SQLModel class
            data: Record data
            
        Returns:
            Created record
        """
        with self._get_session() as session:
            obj = model_class(**data)
            self._update_timestamps(obj, is_create=True)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            logger.info(f"Created {model_class.__name__} with id {obj.id}")
            return obj

    def get_by_id(self, model_class: Type[T], record_id: int) -> Optional[T]:
        """Get a record by ID
        
        Args:
            model_class: SQLModel class
            record_id: Record ID
            
        Returns:
            Record if found, None otherwise
        """
        with self._get_session() as session:
            obj = session.get(model_class, record_id)
            return obj

    def get_all(
        self,
        model_class: Type[T],
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """Get all records with pagination and filtering
        
        Args:
            model_class: SQLModel class
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filters to apply
            
        Returns:
            List of records
        """
        with self._get_session() as session:
            statement = select(model_class)
            
            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    if hasattr(model_class, key) and value is not None:
                        statement = statement.where(getattr(model_class, key) == value)
            
            statement = statement.offset(skip).limit(limit)
            results = session.exec(statement).all()
            return list(results)

    def update(
        self,
        model_class: Type[T],
        record_id: int,
        data: Dict[str, Any]
    ) -> Optional[T]:
        """Update a record
        
        Args:
            model_class: SQLModel class
            record_id: Record ID
            data: Updated data (only non-None values will be updated)
            
        Returns:
            Updated record if found, None otherwise
        """
        with self._get_session() as session:
            obj = session.get(model_class, record_id)
            if not obj:
                return None
            
            # Update only provided fields
            for key, value in data.items():
                if value is not None and hasattr(obj, key):
                    setattr(obj, key, value)
            
            self._update_timestamps(obj, is_create=False)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            logger.info(f"Updated {model_class.__name__} with id {record_id}")
            return obj

    def delete(self, model_class: Type[T], record_id: int) -> bool:
        """Delete a record (soft delete by setting status to 0)
        
        Args:
            model_class: SQLModel class
            record_id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        with self._get_session() as session:
            obj = session.get(model_class, record_id)
            if not obj:
                return False
            
            # Soft delete
            obj.status = 0
            self._update_timestamps(obj, is_create=False)
            session.add(obj)
            session.commit()
            logger.info(f"Deleted (soft) {model_class.__name__} with id {record_id}")
            return True

    def count(self, model_class: Type[T], filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filters
        
        Args:
            model_class: SQLModel class
            filters: Optional filters to apply
            
        Returns:
            Number of records
        """
        with self._get_session() as session:
            statement = select(model_class)
            
            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    if hasattr(model_class, key) and value is not None:
                        statement = statement.where(getattr(model_class, key) == value)
            
            results = session.exec(statement).all()
            return len(results)

    # Dimension-specific methods
    def create_dimension(self, data: Dict[str, Any]) -> MetaDimension:
        """Create a dimension"""
        return self.create(MetaDimension, data)

    def get_dimension(self, dimension_id: int) -> Optional[MetaDimension]:
        """Get a dimension by ID"""
        return self.get_by_id(MetaDimension, dimension_id)

    def get_dimensions(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[int] = None
    ) -> List[MetaDimension]:
        """Get all dimensions"""
        filters = {"status": status} if status is not None else None
        return self.get_all(MetaDimension, skip, limit, filters)

    def update_dimension(
        self,
        dimension_id: int,
        data: Dict[str, Any]
    ) -> Optional[MetaDimension]:
        """Update a dimension"""
        return self.update(MetaDimension, dimension_id, data)

    def delete_dimension(self, dimension_id: int) -> bool:
        """Delete a dimension"""
        return self.delete(MetaDimension, dimension_id)
    
    # Dimension value methods
    def create_dimension_value(self, data: Dict[str, Any]) -> MetaDimensionValue:
        """Create a dimension value"""
        return self.create(MetaDimensionValue, data)
    
    def get_dimension_values(
        self,
        dimension_id: int,
        status: Optional[int] = None
    ) -> List[MetaDimensionValue]:
        """
        Get all values for a specific dimension.
        
        Args:
            dimension_id: ID of the dimension
            status: Optional status filter (1: active, 0: inactive)
            
        Returns:
            List of dimension values
        """
        with self._get_session() as session:
            statement = select(MetaDimensionValue).where(
                MetaDimensionValue.dimension_id == dimension_id
            )
            
            if status is not None:
                statement = statement.where(MetaDimensionValue.status == status)
            
            results = session.exec(statement).all()
            return list(results)
    
    def get_dimension_values_map(
        self,
        dimension_ids: Optional[List[int]] = None,
        status: int = 1
    ) -> Dict[int, set]:
        """
        Get a map of dimension_id to set of values for efficient lookup.
        
        Args:
            dimension_ids: Optional list of dimension IDs to fetch values for.
                          If None, fetches for all dimensions.
            status: Status filter (default: 1 for active values)
            
        Returns:
            Dictionary mapping dimension_id to set of values
        """
        with self._get_session() as session:
            statement = select(MetaDimensionValue).where(
                MetaDimensionValue.status == status
            )
            
            if dimension_ids:
                statement = statement.where(MetaDimensionValue.dimension_id.in_(dimension_ids))
            
            results = session.exec(statement).all()
            
            # Build map
            values_map = {}
            for dim_value in results:
                if dim_value.dimension_id not in values_map:
                    values_map[dim_value.dimension_id] = set()
                values_map[dim_value.dimension_id].add(dim_value.value)
            
            return values_map
    
    def bulk_create_dimension_values(
        self,
        dimension_id: int,
        values: List[str],
        created_by: str = "system"
    ) -> int:
        """
        Bulk create dimension values.
        
        Args:
            dimension_id: ID of the dimension
            values: List of unique values to add
            created_by: User who created the values
            
        Returns:
            Number of values created
        """
        with self._get_session() as session:
            # Get existing values to avoid duplicates
            existing = session.exec(
                select(MetaDimensionValue.value).where(
                    MetaDimensionValue.dimension_id == dimension_id
                )
            ).all()
            existing_values = set(existing)
            
            # Create new values
            count = 0
            for value in values:
                if value not in existing_values:
                    dim_value = MetaDimensionValue(
                        dimension_id=dimension_id,
                        value=value,
                        created_by=created_by,
                        updated_by=created_by
                    )
                    self._update_timestamps(dim_value, is_create=True)
                    session.add(dim_value)
                    count += 1
            
            session.commit()
            logger.info(f"Created {count} dimension values for dimension_id={dimension_id}")
            return count

    # Metric-specific methods
    def create_metric(self, data: Dict[str, Any]) -> MetaMetric:
        """Create a metric"""
        return self.create(MetaMetric, data)

    def get_metric(self, metric_id: int) -> Optional[MetaMetric]:
        """Get a metric by ID"""
        return self.get_by_id(MetaMetric, metric_id)

    def get_metrics(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[int] = None
    ) -> List[MetaMetric]:
        """Get all metrics"""
        filters = {"status": status} if status is not None else None
        return self.get_all(MetaMetric, skip, limit, filters)

    def update_metric(self, metric_id: int, data: Dict[str, Any]) -> Optional[MetaMetric]:
        """Update a metric"""
        return self.update(MetaMetric, metric_id, data)

    def delete_metric(self, metric_id: int) -> bool:
        """Delete a metric"""
        return self.delete(MetaMetric, metric_id)

    # Table-specific methods
    def create_table(self, data: Dict[str, Any]) -> MetaTable:
        """Create a table"""
        return self.create(MetaTable, data)

    def get_table(self, table_id: int) -> Optional[MetaTable]:
        """Get a table by ID"""
        return self.get_by_id(MetaTable, table_id)

    def get_tables(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[int] = None
    ) -> List[MetaTable]:
        """Get all tables"""
        filters = {"status": status} if status is not None else None
        return self.get_all(MetaTable, skip, limit, filters)

    def update_table(self, table_id: int, data: Dict[str, Any]) -> Optional[MetaTable]:
        """Update a table"""
        return self.update(MetaTable, table_id, data)

    def delete_table(self, table_id: int) -> bool:
        """Delete a table"""
        return self.delete(MetaTable, table_id)

    # Entity-specific methods
    def create_entity(self, data: Dict[str, Any]) -> MetaEntity:
        """Create an entity"""
        return self.create(MetaEntity, data)

    def get_entity(self, entity_id: int) -> Optional[MetaEntity]:
        """Get an entity by ID"""
        return self.get_by_id(MetaEntity, entity_id)

    def get_entities(self, skip: int = 0, limit: int = 100) -> List[MetaEntity]:
        """Get all entities"""
        return self.get_all(MetaEntity, skip, limit)

    def update_entity(self, entity_id: int, data: Dict[str, Any]) -> Optional[MetaEntity]:
        """Update an entity"""
        return self.update(MetaEntity, entity_id, data)

    def delete_entity(self, entity_id: int) -> bool:
        """Delete an entity"""
        return self.delete(MetaEntity, entity_id)

    # Database-specific methods
    def create_database(self, data: Dict[str, Any]) -> MetaDatabase:
        """Create a database"""
        return self.create(MetaDatabase, data)

    def get_database(self, database_id: int) -> Optional[MetaDatabase]:
        """Get a database by ID"""
        return self.get_by_id(MetaDatabase, database_id)

    def get_databases(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[int] = None
    ) -> List[MetaDatabase]:
        """Get all databases"""
        filters = {"status": status} if status is not None else None
        return self.get_all(MetaDatabase, skip, limit, filters)

    def update_database(
        self,
        database_id: int,
        data: Dict[str, Any]
    ) -> Optional[MetaDatabase]:
        """Update a database"""
        return self.update(MetaDatabase, database_id, data)

    def delete_database(self, database_id: int) -> bool:
        """Delete a database"""
        return self.delete(MetaDatabase, database_id)

    # Domain-specific methods
    def create_domain(self, data: Dict[str, Any]) -> MetaDomain:
        """Create a domain"""
        return self.create(MetaDomain, data)

    def get_domain(self, domain_id: int) -> Optional[MetaDomain]:
        """Get a domain by ID"""
        return self.get_by_id(MetaDomain, domain_id)

    def get_domains(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[int] = None
    ) -> List[MetaDomain]:
        """Get all domains"""
        filters = {"status": status} if status is not None else None
        return self.get_all(MetaDomain, skip, limit, filters)

    def update_domain(self, domain_id: int, data: Dict[str, Any]) -> Optional[MetaDomain]:
        """Update a domain"""
        return self.update(MetaDomain, domain_id, data)

    def delete_domain(self, domain_id: int) -> bool:
        """Delete a domain"""
        return self.delete(MetaDomain, domain_id)

    # Auto-matching methods
    def sample_field_values(
        self,
        table_id: int,
        field_name: str,
        limit: int = 1000
    ) -> set:
        """
        Sample unique values from a table field.
        
        Note: This is a placeholder implementation. In production, this should
        query the actual data table to get unique values. For now, returns empty set.
        
        Args:
            table_id: ID of the table
            field_name: Name of the field to sample
            limit: Maximum number of unique values to sample
            
        Returns:
            Set of unique field values
        """
        # TODO: Implement actual table querying based on table connection info
        # This would require:
        # 1. Get table metadata (database connection, schema, table name)
        # 2. Connect to the actual database
        # 3. Execute: SELECT DISTINCT field_name FROM table LIMIT limit
        # 4. Return set of values
        
        logger.debug(
            f"Sampling values for field '{field_name}' in table_id={table_id} "
            "(placeholder implementation - returns empty set)"
        )
        return set()
    
    def auto_match_table_dimensions(
        self,
        table_id: int,
        updated_by: str = "system",
        enable_value_matching: bool = False
    ) -> Dict[str, Any]:
        """
        Automatically match all columns of a table to dimensions.
        
        This method:
        1. Gets all columns for the specified table
        2. Gets all active dimensions
        3. Uses DimensionMatcher to find best match for each column
        4. Optionally uses value-based matching if enabled
        5. Updates the column's dimension_id if a match is found
        
        Args:
            table_id: ID of the table whose columns should be matched
            updated_by: User who triggered the auto-matching
            enable_value_matching: Whether to enable value-based matching (Phase 2)
            
        Returns:
            Dictionary with matching statistics:
            - total_columns: Total number of columns processed
            - matched_columns: Number of columns matched to dimensions
            - unmatched_columns: Number of columns without matches
            - updated_columns: Number of columns actually updated
            - value_matched_columns: Number matched via value-based matching
        """
        from app.services.dimension_matcher import DimensionMatcher
        
        with self._get_session() as session:
            # Get all columns for the table
            statement = select(MetaTableColumn).where(MetaTableColumn.table_id == table_id)
            columns = session.exec(statement).all()
            
            if not columns:
                logger.warning(f"No columns found for table_id={table_id}")
                return {
                    "total_columns": 0,
                    "matched_columns": 0,
                    "unmatched_columns": 0,
                    "updated_columns": 0,
                    "value_matched_columns": 0,
                }
            
            # Get all active dimensions
            dimensions = self.get_dimensions(skip=0, limit=10000, status=1)
            
            if not dimensions:
                logger.warning("No active dimensions available for matching")
                return {
                    "total_columns": len(columns),
                    "matched_columns": 0,
                    "unmatched_columns": len(columns),
                    "updated_columns": 0,
                    "value_matched_columns": 0,
                }
            
            # Initialize matcher
            matcher = DimensionMatcher()
            
            # Get dimension values map if value matching is enabled
            dimension_values_map = {}
            if enable_value_matching:
                dimension_ids = [dim.id for dim in dimensions]
                dimension_values_map = self.get_dimension_values_map(
                    dimension_ids=dimension_ids,
                    status=1
                )
                logger.info(
                    f"Loaded dimension values for {len(dimension_values_map)} dimensions"
                )
            
            # Track statistics
            matched_count = 0
            updated_count = 0
            value_matched_count = 0
            
            # Match each column
            for column in columns:
                # Skip if already matched
                if column.dimension_id is not None:
                    logger.debug(f"Column '{column.field_name}' already has dimension_id={column.dimension_id}, skipping")
                    continue
                
                # Try name-based matching first
                matched_dim_id = matcher.auto_match_dimension(column, dimensions)
                
                # If no match and value matching is enabled, try value-based matching
                if not matched_dim_id and enable_value_matching and dimension_values_map:
                    field_values = self.sample_field_values(
                        table_id,
                        column.field_name,
                        limit=matcher.config.VALUE_MATCH_SAMPLE_SIZE
                    )
                    
                    if field_values:
                        # Filter dimensions by semantic type first
                        inferred_semantic_type = matcher.config.infer_semantic_type(column.logical_type)
                        filtered_dimensions = matcher.filter_by_semantic_type(
                            dimensions,
                            inferred_semantic_type
                        )
                        
                        matched_dim_id = matcher.match_by_values(
                            field_values,
                            filtered_dimensions,
                            dimension_values_map
                        )
                        
                        if matched_dim_id:
                            value_matched_count += 1
                            logger.info(
                                f"Value-based match found for column '{column.field_name}'"
                            )
                
                if matched_dim_id:
                    matched_count += 1
                    
                    # Update the column with matched dimension
                    column.dimension_id = matched_dim_id
                    column.updated_by = updated_by
                    self._update_timestamps(column, is_create=False)
                    session.add(column)
                    updated_count += 1
                    
                    logger.info(
                        f"Matched column '{column.field_name}' (id={column.id}) "
                        f"to dimension_id={matched_dim_id}"
                    )
            
            # Commit all updates
            session.commit()
            
            result = {
                "total_columns": len(columns),
                "matched_columns": matched_count,
                "unmatched_columns": len(columns) - matched_count,
                "updated_columns": updated_count,
                "value_matched_columns": value_matched_count,
            }
            
            logger.info(
                f"Auto-matching completed for table_id={table_id}: "
                f"{matched_count} matched out of {len(columns)} columns, "
                f"{updated_count} columns updated, "
                f"{value_matched_count} via value matching"
            )
            
            return result
    
    def get_table_columns(
        self,
        table_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[MetaTableColumn]:
        """
        Get all columns for a specific table.
        
        Args:
            table_id: ID of the table
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of table columns
        """
        with self._get_session() as session:
            statement = select(MetaTableColumn).where(
                MetaTableColumn.table_id == table_id
            ).offset(skip).limit(limit)
            results = session.exec(statement).all()
            return list(results)
