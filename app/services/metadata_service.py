"""Service for metadata management operations"""

import datetime
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlmodel import Session, create_engine, select

from app.models.metadata import (
    MetaDatabase,
    MetaDimension,
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
    def auto_match_table_dimensions(
        self,
        table_id: int,
        updated_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Automatically match all columns of a table to dimensions.
        
        This method:
        1. Gets all columns for the specified table
        2. Gets all active dimensions
        3. Uses DimensionMatcher to find best match for each column
        4. Updates the column's dimension_id if a match is found
        
        Args:
            table_id: ID of the table whose columns should be matched
            updated_by: User who triggered the auto-matching
            
        Returns:
            Dictionary with matching statistics:
            - total_columns: Total number of columns processed
            - matched_columns: Number of columns matched to dimensions
            - unmatched_columns: Number of columns without matches
            - updated_columns: Number of columns actually updated
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
                }
            
            # Initialize matcher
            matcher = DimensionMatcher()
            
            # Track statistics
            matched_count = 0
            updated_count = 0
            
            # Match each column
            for column in columns:
                # Skip if already matched
                if column.dimension_id is not None:
                    logger.debug(f"Column '{column.field_name}' already has dimension_id={column.dimension_id}, skipping")
                    continue
                
                # Try to find a match
                matched_dim_id = matcher.auto_match_dimension(column, dimensions)
                
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
            }
            
            logger.info(
                f"Auto-matching completed for table_id={table_id}: "
                f"{matched_count} matched out of {len(columns)} columns, "
                f"{updated_count} columns updated"
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
