"""Unit tests for configuration loading"""

import pytest
from app.utils.config import Config


@pytest.mark.unit
def test_config_loads_successfully():
    """Test that configuration loads without errors"""
    config = Config()
    assert config is not None


@pytest.mark.unit
def test_config_has_required_sections():
    """Test that configuration has all required sections"""
    config = Config()
    assert hasattr(config, "opensearch")
    assert hasattr(config, "redis")
    assert hasattr(config, "autocomplete")
    assert hasattr(config, "vector")


@pytest.mark.unit
def test_opensearch_config_has_defaults():
    """Test OpenSearch configuration defaults"""
    config = Config()
    assert config.opensearch.get("host") is not None
    assert config.opensearch.get("port") is not None
    assert config.opensearch.get("index_name") is not None


@pytest.mark.unit
def test_autocomplete_weights_are_valid():
    """Test that autocomplete weights are within valid range"""
    config = Config()
    keyword_weight = config.autocomplete.get("keyword_weight", 0.7)
    vector_weight = config.autocomplete.get("vector_weight", 0.3)

    assert 0 <= keyword_weight <= 1
    assert 0 <= vector_weight <= 1
