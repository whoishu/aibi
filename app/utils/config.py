"""Configuration management"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class OpenSearchConfig(BaseModel):
    """OpenSearch configuration"""

    host: str = "localhost"
    port: int = 9200
    use_ssl: bool = False
    verify_certs: bool = False
    username: Optional[str] = None
    password: Optional[str] = None
    index_name: str = "chatbi_autocomplete"


class RedisConfig(BaseModel):
    """Redis configuration"""

    host: str = "localhost"
    port: int = 6379
    db: int = 0


class AutocompleteConfig(BaseModel):
    """Autocomplete service configuration"""

    max_suggestions: int = 10
    min_score: float = 0.1
    keyword_weight: float = 0.7
    vector_weight: float = 0.3
    personalization_weight: float = 0.2
    enable_personalization: bool = True
    enable_prefix_preservation: bool = True


class VectorModelConfig(BaseModel):
    """Vector model configuration"""

    model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    dimension: int = 384


class APIConfig(BaseModel):
    """API configuration"""

    host: str = "0.0.0.0"
    port: int = 8000
    title: str = "ChatBI Autocomplete Service"
    description: str = "Intelligent autocomplete service"
    version: str = "1.0.0"


class LLMConfig(BaseModel):
    """LLM configuration"""

    enabled: bool = False
    provider: str = "openai"
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 150
    api_key: Optional[str] = None


class Config(BaseSettings):
    """Main configuration class"""

    opensearch: OpenSearchConfig = OpenSearchConfig()
    redis: RedisConfig = RedisConfig()
    autocomplete: AutocompleteConfig = AutocompleteConfig()
    vector_model: VectorModelConfig = VectorModelConfig()
    api: APIConfig = APIConfig()
    llm: LLMConfig = LLMConfig()

    @classmethod
    def from_yaml(cls, file_path: str = "config.yaml") -> "Config":
        """Load configuration from YAML file"""
        path = Path(file_path)
        if not path.exists():
            return cls()

        with open(path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)

        return cls(**config_dict)


# Global configuration instance
config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance"""
    global config
    if config is None:
        config = Config.from_yaml()
    return config
