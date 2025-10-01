"""Main FastAPI application"""

import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.utils.config import get_config
from app.services.opensearch_service import OpenSearchService
from app.services.vector_service import VectorService
from app.services.personalization_service import PersonalizationService
from app.services.autocomplete_service import AutocompleteService
from app.api.routes import router, set_autocomplete_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting ChatBI Autocomplete Service...")
    
    # Load configuration
    config = get_config()
    logger.info("Configuration loaded")
    
    # Initialize services
    try:
        # Vector service
        vector_service = VectorService(model_name=config.vector_model.model_name)
        logger.info("Vector service initialized")
        
        # OpenSearch service
        opensearch_service = OpenSearchService(
            host=config.opensearch.host,
            port=config.opensearch.port,
            use_ssl=config.opensearch.use_ssl,
            verify_certs=config.opensearch.verify_certs,
            username=config.opensearch.username,
            password=config.opensearch.password,
            index_name=config.opensearch.index_name,
            vector_dimension=config.vector_model.dimension
        )
        
        # Check connection and create index
        if opensearch_service.check_connection():
            opensearch_service.create_index()
            logger.info("OpenSearch service initialized")
        else:
            logger.warning("OpenSearch not connected - service will have limited functionality")
        
        # Personalization service
        personalization_service = None
        if config.autocomplete.enable_personalization:
            personalization_service = PersonalizationService(
                redis_host=config.redis.host,
                redis_port=config.redis.port,
                redis_db=config.redis.db
            )
            if personalization_service.check_connection():
                logger.info("Personalization service initialized")
            else:
                logger.warning("Redis not connected - personalization disabled")
                personalization_service = None
        
        # Autocomplete service
        autocomplete_service = AutocompleteService(
            opensearch_service=opensearch_service,
            vector_service=vector_service,
            personalization_service=personalization_service,
            keyword_weight=config.autocomplete.keyword_weight,
            vector_weight=config.autocomplete.vector_weight,
            personalization_weight=config.autocomplete.personalization_weight,
            enable_personalization=config.autocomplete.enable_personalization
        )
        
        # Set global service
        set_autocomplete_service(autocomplete_service)
        logger.info("Autocomplete service initialized")
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down ChatBI Autocomplete Service...")


# Create FastAPI app
config = get_config()
app = FastAPI(
    title=config.api.title,
    description=config.api.description,
    version=config.api.version,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["autocomplete"])

# Serve frontend static files if they exist
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists() and frontend_dist.is_dir():
    # Mount static files (CSS, JS, etc.)
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")
    
    @app.get("/demo")
    async def serve_frontend():
        """Serve the frontend demo page"""
        return FileResponse(str(frontend_dist / "index.html"))
    
    @app.get("/demo/{path:path}")
    async def serve_frontend_catchall(path: str):
        """Serve index.html for any unmatched frontend route under /demo"""
        return FileResponse(str(frontend_dist / "index.html"))
    
    logger.info(f"Frontend demo available at /demo")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ChatBI Autocomplete Service",
        "version": config.api.version,
        "status": "running",
        "demo": "/demo" if frontend_dist.exists() else None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.api.host,
        port=config.api.port,
        reload=True
    )
