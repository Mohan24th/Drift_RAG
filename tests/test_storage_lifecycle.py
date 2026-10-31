import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from app.storage.local import LocalDocumentStorage
from app.storage.supabase import SupabaseDocumentStorage

def test_local_storage_persistence():
    """Verify that LocalDocumentStorage save does NOT place files in temp dir."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        storage = LocalDocumentStorage(base_dir=str(tmp_path))
        
        # Create a dummy source file
        source = tmp_path / "source.pdf"
        source.write_text("content")
        
        storage_path = storage.save(
            source_path=str(source),
            document_id="doc1",
            version_number=1,
            filename="test.pdf"
        )
        
        # The stored path should NOT be in the system temp dir
        # Note: tmp_path is a TemporaryDirectory, but the check in app/api/routes/documents.py 
        # is against tempfile.gettempdir().
        # We verify that as long as base_dir is not the system temp dir, it's preserved.
        assert Path(storage_path).parent != Path(tempfile.gettempdir())
        assert Path(storage_path).exists()

def test_supabase_storage_temp_nature():
    """Verify that SupabaseDocumentStorage.get_local_path creates files in temp dir."""
    # Mock Supabase client
    mock_client = MagicMock()
    storage = SupabaseDocumentStorage(
        supabase_url="http://fake",
        service_key="fake",
        bucket="fake"
    )
    storage.client = mock_client
    mock_client.storage.from_().download.return_value = b"content"
    
    local_path = storage.get_local_path("remote/path.pdf")
    
    # The downloaded path SHOULD be in the system temp dir
    assert Path(local_path).parent == Path(tempfile.gettempdir())
    
    # Cleanup
    Path(local_path).unlink(missing_ok=True)
