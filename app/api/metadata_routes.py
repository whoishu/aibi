"""API routes for metadata management"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.metadata_schemas import (
    DatabaseCreate,
    DatabaseResponse,
    DatabaseUpdate,
    DimensionCreate,
    DimensionResponse,
    DimensionUpdate,
    DomainCreate,
    DomainResponse,
    DomainUpdate,
    EntityCreate,
    EntityResponse,
    EntityUpdate,
    MetricCreate,
    MetricResponse,
    MetricUpdate,
    TableCreate,
    TableResponse,
    TableUpdate,
    DimensionMappingRequest,
    DimensionMappingSuggestionResponse,
    ApplyDimensionMappingRequest,
    ApplyDimensionMappingResponse,
)
from app.services.metadata_service import MetadataService
from app.services.dimension_mapping_service import DimensionMappingService

logger = logging.getLogger(__name__)

router = APIRouter()

# Global service instance
_metadata_service: Optional[MetadataService] = None


def get_metadata_service() -> MetadataService:
    """Dependency to get metadata service"""
    if _metadata_service is None:
        raise HTTPException(status_code=503, detail="Metadata service not initialized")
    return _metadata_service


def set_metadata_service(service: MetadataService):
    """Set the global metadata service instance"""
    global _metadata_service
    _metadata_service = service


# Dimension endpoints
@router.post("/dimensions", response_model=DimensionResponse, status_code=201)
async def create_dimension(
    dimension: DimensionCreate,
    service: MetadataService = Depends(get_metadata_service)
):
    """Create a new dimension"""
    try:
        result = service.create_dimension(dimension.dict())
        return DimensionResponse.from_orm(result)
    except Exception as e:
        logger.error(f"Error creating dimension: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dimensions/{dimension_id}", response_model=DimensionResponse)
async def get_dimension(
    dimension_id: int,
    service: MetadataService = Depends(get_metadata_service)
):
    """Get a dimension by ID"""
    result = service.get_dimension(dimension_id)
    if not result:
        raise HTTPException(status_code=404, detail="Dimension not found")
    return DimensionResponse.from_orm(result)


@router.get("/dimensions", response_model=dict)
async def list_dimensions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[int] = Query(None, description="Filter by status (1=active, 0=inactive)"),
    service: MetadataService = Depends(get_metadata_service)
):
    """List all dimensions with pagination"""
    try:
        items = service.get_dimensions(skip=skip, limit=limit, status=status)
        total = service.count(service.get_dimension.__self__.__class__.__bases__[0])
        return {
            "items": [DimensionResponse.from_orm(item) for item in items],
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit
        }
    except Exception as e:
        logger.error(f"Error listing dimensions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/dimensions/{dimension_id}", response_model=DimensionResponse)
async def update_dimension(
    dimension_id: int,
    dimension: DimensionUpdate,
    service: MetadataService = Depends(get_metadata_service)
):
    """Update a dimension"""
    try:
        result = service.update_dimension(dimension_id, dimension.dict(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail="Dimension not found")
        return DimensionResponse.from_orm(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating dimension: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/dimensions/{dimension_id}", status_code=204)
async def delete_dimension(
    dimension_id: int,
    service: MetadataService = Depends(get_metadata_service)
):
    """Delete a dimension (soft delete)"""
    success = service.delete_dimension(dimension_id)
    if not success:
        raise HTTPException(status_code=404, detail="Dimension not found")
    return None


# Metric endpoints
@router.post("/metrics", response_model=MetricResponse, status_code=201)
async def create_metric(
    metric: MetricCreate,
    service: MetadataService = Depends(get_metadata_service)
):
    """Create a new metric"""
    try:
        result = service.create_metric(metric.dict())
        return MetricResponse.from_orm(result)
    except Exception as e:
        logger.error(f"Error creating metric: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/{metric_id}", response_model=MetricResponse)
async def get_metric(
    metric_id: int,
    service: MetadataService = Depends(get_metadata_service)
):
    """Get a metric by ID"""
    result = service.get_metric(metric_id)
    if not result:
        raise HTTPException(status_code=404, detail="Metric not found")
    return MetricResponse.from_orm(result)


@router.get("/metrics", response_model=dict)
async def list_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[int] = Query(None, description="Filter by status (1=active, 0=inactive)"),
    service: MetadataService = Depends(get_metadata_service)
):
    """List all metrics with pagination"""
    try:
        items = service.get_metrics(skip=skip, limit=limit, status=status)
        total = service.count(service.get_metric.__self__.__class__.__bases__[0])
        return {
            "items": [MetricResponse.from_orm(item) for item in items],
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit
        }
    except Exception as e:
        logger.error(f"Error listing metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/metrics/{metric_id}", response_model=MetricResponse)
async def update_metric(
    metric_id: int,
    metric: MetricUpdate,
    service: MetadataService = Depends(get_metadata_service)
):
    """Update a metric"""
    try:
        result = service.update_metric(metric_id, metric.dict(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail="Metric not found")
        return MetricResponse.from_orm(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating metric: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/metrics/{metric_id}", status_code=204)
async def delete_metric(
    metric_id: int,
    service: MetadataService = Depends(get_metadata_service)
):
    """Delete a metric (soft delete)"""
    success = service.delete_metric(metric_id)
    if not success:
        raise HTTPException(status_code=404, detail="Metric not found")
    return None


# Table endpoints
@router.post("/tables", response_model=TableResponse, status_code=201)
async def create_table(
    table: TableCreate,
    service: MetadataService = Depends(get_metadata_service)
):
    """Create a new table"""
    try:
        result = service.create_table(table.dict())
        return TableResponse.from_orm(result)
    except Exception as e:
        logger.error(f"Error creating table: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables/{table_id}", response_model=TableResponse)
async def get_table(
    table_id: int,
    service: MetadataService = Depends(get_metadata_service)
):
    """Get a table by ID"""
    result = service.get_table(table_id)
    if not result:
        raise HTTPException(status_code=404, detail="Table not found")
    return TableResponse.from_orm(result)


@router.get("/tables", response_model=dict)
async def list_tables(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[int] = Query(None, description="Filter by status (1=active, 0=inactive)"),
    service: MetadataService = Depends(get_metadata_service)
):
    """List all tables with pagination"""
    try:
        items = service.get_tables(skip=skip, limit=limit, status=status)
        total = service.count(service.get_table.__self__.__class__.__bases__[0])
        return {
            "items": [TableResponse.from_orm(item) for item in items],
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit
        }
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/tables/{table_id}", response_model=TableResponse)
async def update_table(
    table_id: int,
    table: TableUpdate,
    service: MetadataService = Depends(get_metadata_service)
):
    """Update a table"""
    try:
        result = service.update_table(table_id, table.dict(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail="Table not found")
        return TableResponse.from_orm(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating table: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tables/{table_id}", status_code=204)
async def delete_table(
    table_id: int,
    service: MetadataService = Depends(get_metadata_service)
):
    """Delete a table (soft delete)"""
    success = service.delete_table(table_id)
    if not success:
        raise HTTPException(status_code=404, detail="Table not found")
    return None


# Entity endpoints
@router.post("/entities", response_model=EntityResponse, status_code=201)
async def create_entity(
    entity: EntityCreate,
    service: MetadataService = Depends(get_metadata_service)
):
    """Create a new entity"""
    try:
        result = service.create_entity(entity.dict())
        return EntityResponse.from_orm(result)
    except Exception as e:
        logger.error(f"Error creating entity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: int,
    service: MetadataService = Depends(get_metadata_service)
):
    """Get an entity by ID"""
    result = service.get_entity(entity_id)
    if not result:
        raise HTTPException(status_code=404, detail="Entity not found")
    return EntityResponse.from_orm(result)


@router.get("/entities", response_model=dict)
async def list_entities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: MetadataService = Depends(get_metadata_service)
):
    """List all entities with pagination"""
    try:
        items = service.get_entities(skip=skip, limit=limit)
        total = service.count(service.get_entity.__self__.__class__.__bases__[0])
        return {
            "items": [EntityResponse.from_orm(item) for item in items],
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit
        }
    except Exception as e:
        logger.error(f"Error listing entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/entities/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: int,
    entity: EntityUpdate,
    service: MetadataService = Depends(get_metadata_service)
):
    """Update an entity"""
    try:
        result = service.update_entity(entity_id, entity.dict(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail="Entity not found")
        return EntityResponse.from_orm(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating entity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/entities/{entity_id}", status_code=204)
async def delete_entity(
    entity_id: int,
    service: MetadataService = Depends(get_metadata_service)
):
    """Delete an entity (soft delete)"""
    success = service.delete_entity(entity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entity not found")
    return None


# Database endpoints
@router.post("/databases", response_model=DatabaseResponse, status_code=201)
async def create_database(
    database: DatabaseCreate,
    service: MetadataService = Depends(get_metadata_service)
):
    """Create a new database"""
    try:
        result = service.create_database(database.dict())
        return DatabaseResponse.from_orm(result)
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/databases/{database_id}", response_model=DatabaseResponse)
async def get_database(
    database_id: int,
    service: MetadataService = Depends(get_metadata_service)
):
    """Get a database by ID"""
    result = service.get_database(database_id)
    if not result:
        raise HTTPException(status_code=404, detail="Database not found")
    return DatabaseResponse.from_orm(result)


@router.get("/databases", response_model=dict)
async def list_databases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[int] = Query(None, description="Filter by status (1=active, 0=inactive)"),
    service: MetadataService = Depends(get_metadata_service)
):
    """List all databases with pagination"""
    try:
        items = service.get_databases(skip=skip, limit=limit, status=status)
        total = service.count(service.get_database.__self__.__class__.__bases__[0])
        return {
            "items": [DatabaseResponse.from_orm(item) for item in items],
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit
        }
    except Exception as e:
        logger.error(f"Error listing databases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/databases/{database_id}", response_model=DatabaseResponse)
async def update_database(
    database_id: int,
    database: DatabaseUpdate,
    service: MetadataService = Depends(get_metadata_service)
):
    """Update a database"""
    try:
        result = service.update_database(database_id, database.dict(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail="Database not found")
        return DatabaseResponse.from_orm(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/databases/{database_id}", status_code=204)
async def delete_database(
    database_id: int,
    service: MetadataService = Depends(get_metadata_service)
):
    """Delete a database (soft delete)"""
    success = service.delete_database(database_id)
    if not success:
        raise HTTPException(status_code=404, detail="Database not found")
    return None


# Domain endpoints
@router.post("/domains", response_model=DomainResponse, status_code=201)
async def create_domain(
    domain: DomainCreate,
    service: MetadataService = Depends(get_metadata_service)
):
    """Create a new domain"""
    try:
        result = service.create_domain(domain.dict())
        return DomainResponse.from_orm(result)
    except Exception as e:
        logger.error(f"Error creating domain: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/domains/{domain_id}", response_model=DomainResponse)
async def get_domain(
    domain_id: int,
    service: MetadataService = Depends(get_metadata_service)
):
    """Get a domain by ID"""
    result = service.get_domain(domain_id)
    if not result:
        raise HTTPException(status_code=404, detail="Domain not found")
    return DomainResponse.from_orm(result)


@router.get("/domains", response_model=dict)
async def list_domains(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[int] = Query(None, description="Filter by status (1=active, 0=inactive)"),
    service: MetadataService = Depends(get_metadata_service)
):
    """List all domains with pagination"""
    try:
        items = service.get_domains(skip=skip, limit=limit, status=status)
        total = service.count(service.get_domain.__self__.__class__.__bases__[0])
        return {
            "items": [DomainResponse.from_orm(item) for item in items],
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit
        }
    except Exception as e:
        logger.error(f"Error listing domains: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/domains/{domain_id}", response_model=DomainResponse)
async def update_domain(
    domain_id: int,
    domain: DomainUpdate,
    service: MetadataService = Depends(get_metadata_service)
):
    """Update a domain"""
    try:
        result = service.update_domain(domain_id, domain.dict(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail="Domain not found")
        return DomainResponse.from_orm(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating domain: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/domains/{domain_id}", status_code=204)
async def delete_domain(
    domain_id: int,
    service: MetadataService = Depends(get_metadata_service)
):
    """Delete a domain (soft delete)"""
    success = service.delete_domain(domain_id)
    if not success:
        raise HTTPException(status_code=404, detail="Domain not found")
    return None


# Dimension mapping endpoints
@router.post("/dimension-mapping/suggest", response_model=DimensionMappingSuggestionResponse)
async def suggest_dimension_mappings(
    request: DimensionMappingRequest,
    service: MetadataService = Depends(get_metadata_service)
):
    """
    Suggest dimension mappings for table columns
    
    This endpoint analyzes table columns and suggests candidate dimensions based on:
    - Exact name matching
    - Alias matching
    - Fuzzy matching (using Levenshtein distance)
    - Value-based matching (if dimension values are provided)
    - Semantic type compatibility
    
    Returns a scored list of candidate dimensions for each unmapped column.
    """
    try:
        with service._get_session() as session:
            mapping_service = DimensionMappingService(session)
            suggestions = mapping_service.suggest_dimension_mappings(
                table_id=request.table_id,
                max_candidates=request.max_candidates,
                min_score=request.min_score
            )
            
            return DimensionMappingSuggestionResponse(
                table_id=request.table_id,
                suggestions=suggestions
            )
    except Exception as e:
        logger.error(f"Error suggesting dimension mappings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dimension-mapping/apply", response_model=ApplyDimensionMappingResponse)
async def apply_dimension_mapping(
    request: ApplyDimensionMappingRequest,
    service: MetadataService = Depends(get_metadata_service)
):
    """
    Apply a dimension mapping to a table column
    
    This endpoint assigns a dimension to a table column based on user confirmation
    of the suggested mapping.
    """
    try:
        with service._get_session() as session:
            mapping_service = DimensionMappingService(session)
            success = mapping_service.apply_dimension_mapping(
                column_id=request.column_id,
                dimension_id=request.dimension_id,
                updated_by=request.updated_by
            )
            
            if success:
                return ApplyDimensionMappingResponse(
                    success=True,
                    message=f"Successfully mapped column {request.column_id} to dimension {request.dimension_id}"
                )
            else:
                return ApplyDimensionMappingResponse(
                    success=False,
                    message="Failed to apply dimension mapping. Column or dimension not found."
                )
    except Exception as e:
        logger.error(f"Error applying dimension mapping: {e}")
        raise HTTPException(status_code=500, detail=str(e))
