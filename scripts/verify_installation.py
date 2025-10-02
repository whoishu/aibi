"""Verification script to check if the installation is correct"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def verify_imports():
    """Verify all imports work"""
    print("Verifying imports...")

    try:
        # Test basic imports
        from app import __version__

        print(f"✓ App version: {__version__}")

        # Test models
        from app.models.schemas import AutocompleteRequest, AutocompleteResponse, Suggestion

        print("✓ Models imported successfully")

        # Test config
        from app.utils.config import Config, get_config

        print("✓ Config imported successfully")

        # Test services (without initializing connections)
        from app.services.autocomplete_service import AutocompleteService
        from app.services.opensearch_service import OpenSearchService
        from app.services.personalization_service import PersonalizationService
        from app.services.vector_service import VectorService

        print("✓ Services imported successfully")

        # Test API
        from app.api.routes import router

        print("✓ API routes imported successfully")

        # Test main
        from app.main import app

        print("✓ FastAPI app imported successfully")

        return True

    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def verify_config():
    """Verify configuration loading"""
    print("\nVerifying configuration...")

    try:
        from app.utils.config import get_config

        config = get_config()
        print(f"✓ OpenSearch host: {config.opensearch.host}:{config.opensearch.port}")
        print(f"✓ Redis host: {config.redis.host}:{config.redis.port}")
        print(f"✓ API host: {config.api.host}:{config.api.port}")
        print(f"✓ Vector model: {config.vector_model.model_name}")
        print(f"✓ Keyword weight: {config.autocomplete.keyword_weight}")
        print(f"✓ Vector weight: {config.autocomplete.vector_weight}")

        return True

    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def verify_models():
    """Verify data models"""
    print("\nVerifying data models...")

    try:
        from app.models.schemas import AutocompleteRequest, AutocompleteResponse, Suggestion

        # Test request model
        request = AutocompleteRequest(query="test", user_id="user1", limit=5)
        print(
            f"✓ Request model: query='{request.query}', user_id='{request.user_id}', limit={request.limit}"
        )

        # Test suggestion model
        suggestion = Suggestion(text="test suggestion", score=0.95, source="keyword")
        print(f"✓ Suggestion model: text='{suggestion.text}', score={suggestion.score}")

        # Test response model
        response = AutocompleteResponse(query="test", suggestions=[suggestion], total=1)
        print(f"✓ Response model: query='{response.query}', total={response.total}")

        return True

    except Exception as e:
        print(f"✗ Model validation error: {e}")
        return False


def verify_file_structure():
    """Verify file structure"""
    print("\nVerifying file structure...")

    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/api/__init__.py",
        "app/api/routes.py",
        "app/models/__init__.py",
        "app/models/schemas.py",
        "app/services/__init__.py",
        "app/services/autocomplete_service.py",
        "app/services/opensearch_service.py",
        "app/services/vector_service.py",
        "app/services/personalization_service.py",
        "app/utils/__init__.py",
        "app/utils/config.py",
        "config.yaml",
        "requirements.txt",
        "README.md",
        ".gitignore",
        "docker-compose.yml",
        "scripts/init_data.py",
        "scripts/test_api.py",
        "examples/client_example.py",
    ]

    base_path = os.path.join(os.path.dirname(__file__), "..")

    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - NOT FOUND")
            all_exist = False

    return all_exist


def main():
    """Main verification function"""
    print("=" * 60)
    print("ChatBI Autocomplete Service - Installation Verification")
    print("=" * 60)

    results = []

    # Run verifications
    results.append(("Imports", verify_imports()))
    results.append(("Configuration", verify_config()))
    results.append(("Data Models", verify_models()))
    results.append(("File Structure", verify_file_structure()))

    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n✓ All verifications passed!")
        print("\nNext steps:")
        print("1. Start dependencies: docker-compose up -d")
        print("2. Initialize data: python scripts/init_data.py")
        print("3. Start service: python app/main.py")
        print("4. Test API: python scripts/test_api.py")
        return 0
    else:
        print("\n✗ Some verifications failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
