"""OpenSearch service for hybrid search"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from opensearchpy import OpenSearch, helpers
from opensearchpy.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class OpenSearchService:
    """Service for interacting with OpenSearch"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 9200,
        use_ssl: bool = False,
        verify_certs: bool = False,
        username: Optional[str] = None,
        password: Optional[str] = None,
        index_name: str = "chatbi_autocomplete",
        vector_dimension: int = 384
    ):
        """Initialize OpenSearch client
        
        Args:
            host: OpenSearch host
            port: OpenSearch port
            use_ssl: Whether to use SSL
            verify_certs: Whether to verify certificates
            username: Username for authentication
            password: Password for authentication
            index_name: Name of the index
            vector_dimension: Dimension of vector embeddings
        """
        self.index_name = index_name
        self.vector_dimension = vector_dimension
        
        # Build client configuration
        client_config = {
            "hosts": [{"host": host, "port": port}],
            "use_ssl": use_ssl,
            "verify_certs": verify_certs,
        }
        
        if username and password:
            client_config["http_auth"] = (username, password)
        
        self.client = OpenSearch(**client_config)
        logger.info(f"OpenSearch client initialized for index: {index_name}")
    
    def check_connection(self) -> bool:
        """Check if OpenSearch is connected
        
        Returns:
            True if connected, False otherwise
        """
        try:
            info = self.client.info()
            logger.info(f"OpenSearch connected: {info['version']['number']}")
            return True
        except Exception as e:
            logger.error(f"OpenSearch connection failed: {e}")
            return False
    
    def create_index(self) -> bool:
        """Create the autocomplete index with proper mappings
        
        Returns:
            True if index created or already exists, False otherwise
        """
        try:
            if self.client.indices.exists(index=self.index_name):
                logger.info(f"Index {self.index_name} already exists")
                return True
            
            # Define index settings and mappings
            index_body = {
                "settings": {
                    "index": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0,
                        "knn": True,
                        "knn.space_type": "cosinesimil"
                    },
                    "analysis": {
                        "analyzer": {
                            "ik_smart_pinyin": {
                                "type": "custom",
                                "tokenizer": "ik_smart"
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "text": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                },
                                "completion": {
                                    "type": "completion"
                                }
                            }
                        },
                        "keywords": {
                            "type": "keyword"
                        },
                        "vector": {
                            "type": "knn_vector",
                            "dimension": self.vector_dimension
                        },
                        "metadata": {
                            "type": "object",
                            "enabled": True
                        },
                        "frequency": {
                            "type": "integer"
                        },
                        "created_at": {
                            "type": "date"
                        },
                        "updated_at": {
                            "type": "date"
                        }
                    }
                }
            }
            
            self.client.indices.create(index=self.index_name, body=index_body)
            logger.info(f"Index {self.index_name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return False
    
    def index_document(
        self,
        doc_id: str,
        text: str,
        vector: List[float],
        keywords: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Index a single document
        
        Args:
            doc_id: Document ID
            text: Document text
            vector: Vector embedding
            keywords: List of keywords
            metadata: Additional metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from datetime import datetime
            
            doc = {
                "text": text,
                "vector": vector,
                "keywords": keywords or [],
                "metadata": metadata or {},
                "frequency": 0,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            self.client.index(
                index=self.index_name,
                id=doc_id,
                body=doc,
                refresh=True
            )
            logger.info(f"Document {doc_id} indexed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index document: {e}")
            return False
    
    def bulk_index_documents(self, documents: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Bulk index multiple documents
        
        Args:
            documents: List of documents to index
            
        Returns:
            Tuple of (success_count, error_count)
        """
        try:
            from datetime import datetime
            
            actions = []
            for doc in documents:
                action = {
                    "_index": self.index_name,
                    "_id": doc.get("doc_id", None),
                    "_source": {
                        "text": doc["text"],
                        "vector": doc["vector"],
                        "keywords": doc.get("keywords", []),
                        "metadata": doc.get("metadata", {}),
                        "frequency": 0,
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                }
                actions.append(action)
            
            success, errors = helpers.bulk(self.client, actions, refresh=True)
            logger.info(f"Bulk indexed {success} documents with {len(errors)} errors")
            return success, len(errors)
            
        except Exception as e:
            logger.error(f"Bulk indexing failed: {e}")
            return 0, len(documents)
    
    def keyword_search(
        self,
        query: str,
        size: int = 10,
        min_score: float = 0.1
    ) -> List[Dict[str, Any]]:
        """Perform keyword-based search
        
        Args:
            query: Search query
            size: Number of results
            min_score: Minimum score threshold
            
        Returns:
            List of search results
        """
        try:
            # Multi-match query for keyword search
            search_body = {
                "query": {
                    "bool": {
                        "should": [
                            {
                                "match_phrase_prefix": {
                                    "text": {
                                        "query": query,
                                        "boost": 3.0
                                    }
                                }
                            },
                            {
                                "match": {
                                    "text": {
                                        "query": query,
                                        "boost": 2.0,
                                        "fuzziness": "AUTO"
                                    }
                                }
                            },
                            {
                                "term": {
                                    "keywords": {
                                        "value": query,
                                        "boost": 4.0
                                    }
                                }
                            }
                        ],
                        "minimum_should_match": 1
                    }
                },
                "size": size,
                "min_score": min_score
            }
            
            response = self.client.search(index=self.index_name, body=search_body)
            
            results = []
            for hit in response["hits"]["hits"]:
                results.append({
                    "doc_id": hit["_id"],
                    "text": hit["_source"]["text"],
                    "score": hit["_score"],
                    "keywords": hit["_source"].get("keywords", []),
                    "metadata": hit["_source"].get("metadata", {})
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []
    
    def vector_search(
        self,
        query_vector: List[float],
        size: int = 10,
        min_score: float = 0.1
    ) -> List[Dict[str, Any]]:
        """Perform vector-based search
        
        Args:
            query_vector: Query vector embedding
            size: Number of results
            min_score: Minimum score threshold
            
        Returns:
            List of search results
        """
        try:
            search_body = {
                "query": {
                    "knn": {
                        "vector": {
                            "vector": query_vector,
                            "k": size
                        }
                    }
                },
                "size": size,
                "min_score": min_score
            }
            
            response = self.client.search(index=self.index_name, body=search_body)
            
            results = []
            for hit in response["hits"]["hits"]:
                results.append({
                    "doc_id": hit["_id"],
                    "text": hit["_source"]["text"],
                    "score": hit["_score"],
                    "keywords": hit["_source"].get("keywords", []),
                    "metadata": hit["_source"].get("metadata", {})
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def hybrid_search(
        self,
        query: str,
        query_vector: List[float],
        size: int = 10,
        keyword_weight: float = 0.7,
        vector_weight: float = 0.3,
        min_score: float = 0.1
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search combining keyword and vector search
        
        Args:
            query: Search query text
            query_vector: Query vector embedding
            size: Number of results
            keyword_weight: Weight for keyword search
            vector_weight: Weight for vector search
            min_score: Minimum score threshold
            
        Returns:
            List of search results with combined scores
        """
        # Get results from both searches
        keyword_results = self.keyword_search(query, size=size*2, min_score=0)
        vector_results = self.vector_search(query_vector, size=size*2, min_score=0)
        
        # Combine results
        combined_scores: Dict[str, Dict[str, Any]] = {}
        
        # Process keyword results
        for result in keyword_results:
            doc_id = result["doc_id"]
            combined_scores[doc_id] = {
                "text": result["text"],
                "keyword_score": result["score"],
                "vector_score": 0.0,
                "keywords": result["keywords"],
                "metadata": result["metadata"]
            }
        
        # Process vector results
        for result in vector_results:
            doc_id = result["doc_id"]
            if doc_id in combined_scores:
                combined_scores[doc_id]["vector_score"] = result["score"]
            else:
                combined_scores[doc_id] = {
                    "text": result["text"],
                    "keyword_score": 0.0,
                    "vector_score": result["score"],
                    "keywords": result["keywords"],
                    "metadata": result["metadata"]
                }
        
        # Calculate combined scores and filter
        final_results = []
        for doc_id, data in combined_scores.items():
            combined_score = (
                data["keyword_score"] * keyword_weight +
                data["vector_score"] * vector_weight
            )
            
            if combined_score >= min_score:
                final_results.append({
                    "doc_id": doc_id,
                    "text": data["text"],
                    "score": combined_score,
                    "keyword_score": data["keyword_score"],
                    "vector_score": data["vector_score"],
                    "keywords": data["keywords"],
                    "metadata": data["metadata"]
                })
        
        # Sort by score and return top results
        final_results.sort(key=lambda x: x["score"], reverse=True)
        return final_results[:size]
    
    def update_frequency(self, doc_id: str, increment: int = 1) -> bool:
        """Update document frequency (usage tracking)
        
        Args:
            doc_id: Document ID
            increment: Amount to increment frequency by
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from datetime import datetime
            
            self.client.update(
                index=self.index_name,
                id=doc_id,
                body={
                    "script": {
                        "source": "ctx._source.frequency += params.increment",
                        "params": {"increment": increment}
                    },
                    "doc": {
                        "updated_at": datetime.now().isoformat()
                    }
                }
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to update frequency: {e}")
            return False
