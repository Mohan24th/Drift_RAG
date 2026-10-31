import os
import pytest
from unittest.mock import MagicMock
from app.database.document_service import DocumentService
from app.ingestion.service import IngestionService
from app.retrieval.embeddings import EmbeddingModel
from app.config import settings

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def mock_emb():
    emb = MagicMock()
    # Mock encode to return a numpy-like object that has .tolist()
    class MockArray:
        def __init__(self, data):
            self.data = data
        def tolist(self):
            return self.data
            
    emb.encode.return_value = [MockArray([0.1] * 384)]
    return emb

@pytest.fixture
def service(mock_repo, mock_emb):
    session = MagicMock()
    ingestion = IngestionService()
    return DocumentService(mock_repo, ingestion, mock_emb, session)

def test_document_service_uses_config_chunk_size(service, mock_repo):
    """Verify that DocumentService respects the global settings.chunk_size."""
    
    original_size = settings.chunk_size
    settings.chunk_size = 1000
    
    try:
        mock_repo.get_document_by_name.return_value = MagicMock(id="doc1", name="test")
        mock_repo.get_version.return_value = None
        mock_repo.get_latest_version.return_value = None
        
        with open("test_chunk_config.txt", "w") as f:
            f.write("A" * 2000)
            
        result = service.ingest_document(
            file_path="test_chunk_config.txt",
            document_name="test",
            version_number=1
        )
        
        first_chunk_text = result["chunks"][0].text
        assert len(first_chunk_text) > 500
        assert len(first_chunk_text) <= 1000 + 100
        
    finally:
        settings.chunk_size = original_size
        if os.path.exists("test_chunk_config.txt"):
            os.remove("test_chunk_config.txt")

def test_document_service_explicit_override(service, mock_repo):
    """Verify that an explicitly provided chunk_size overrides the configuration."""
    
    settings.chunk_size = 1000
    
    # Reset mock for the second test to avoid "Version v1 already exists"
    mock_repo.get_version.return_value = None
    mock_repo.get_latest_version.return_value = None
    
    with open("test_override.txt", "w") as f:
        f.write("A" * 2000)
        
    result = service.ingest_document(
        file_path="test_override.txt",
        document_name="override",
        version_number=1,
        chunk_size=100
    )
    
    first_chunk_text = result["chunks"][0].text
    assert len(first_chunk_text) <= 100 + 50
    assert len(first_chunk_text) < 1000
    
    if os.path.exists("test_override.txt"):
        os.remove("test_override.txt")
