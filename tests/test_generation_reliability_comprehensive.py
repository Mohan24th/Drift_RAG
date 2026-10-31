import pytest
from unittest.mock import MagicMock, patch
from app.generation.qa import RAGAnswerer
from app.generation.llm import LLM
from app.retrieval.pg_retriever import PgRetriever
from app.generation.models import RAGResponse

# --- Mocks and Helpers ---

class MockChunk:
    def __init__(self, text, index):
        self.text = text
        self.chunk_index = index
        self.id = "chunk_id"

class MockVersion:
    def __init__(self, number):
        self.version_number = number
        self.id = "ver_id"

class MockDocument:
    def __init__(self, name):
        self.name = name
        self.id = "doc_id"

def create_mock_results(num_chunks=3):
    return [
        (MockChunk(f"Text {i}", i), MockVersion(1), MockDocument("Doc"), 0.9 - (i*0.1))
        for i in range(num_chunks)
    ]

# --- Tests ---

def test_empty_retrieval_abstention():
    """Test 1: Verify behavior when no chunks are retrieved."""
    mock_retriever = MagicMock(spec=PgRetriever)
    mock_retriever.retrieve.return_value = []
    mock_llm = MagicMock(spec=LLM)
    
    answerer = RAGAnswerer(mock_retriever, mock_llm)
    response = answerer.answer("Question", "ver_1")
    
    assert "I don't have enough information" in response.answer
    assert response.sources == []
    mock_llm.generate.assert_not_called()

def test_irrelevant_context_abstention():
    """Test 2: Verify abstention when LLM finds no answer in context."""
    mock_retriever = MagicMock(spec=PgRetriever)
    mock_retriever.retrieve.return_value = create_mock_results(1)
    
    mock_llm = MagicMock(spec=LLM)
    # Mock the LLM following the system prompt to abstain
    mock_llm.generate.return_value = ("I do not have enough information in the context to answer this.", "test-model")
    
    answerer = RAGAnswerer(mock_retriever, mock_llm)
    response = answerer.answer("Question", "ver_1")
    
    assert "do not have enough information" in response.answer.lower()
    assert len(response.sources) == 1

def test_partial_relevance_and_citations():
    """Test 3: Verify citations map correctly to the specific supporting chunks."""
    mock_retriever = MagicMock(spec=PgRetriever)
    mock_retriever.retrieve.return_value = create_mock_results(3)
    
    mock_llm = MagicMock(spec=LLM)
    # LLM only cites the first and third chunk
    mock_llm.generate.return_value = ("The answer is a mix of [1] and [3].", "test-model")
    
    answerer = RAGAnswerer(mock_retriever, mock_llm)
    response = answerer.answer("Question", "ver_1")
    
    assert "[1]" in response.answer and "[3]" in response.answer
    assert "[2]" not in response.answer
    # Metadata should still contain all retrieved chunks as candidates
    assert len(response.sources) == 3

def test_citation_integrity_and_validation(caplog):
    """Test 4: Verify citation identifiers are validated against included chunks."""
    mock_retriever = MagicMock(spec=PgRetriever)
    mock_retriever.retrieve.return_value = create_mock_results(2) # Only [1] and [2]
    
    mock_llm = MagicMock(spec=LLM)
    # LLM invents [99]
    mock_llm.generate.return_value = ("The answer is [1] and [99].", "test-model")
    
    answerer = RAGAnswerer(mock_retriever, mock_llm)
    answerer.answer("Question", "ver_1")
    
    assert "LLM invented citations: ['[99]']" in caplog.text

def test_version_isolation_metadata():
    """Test 5: Verify metadata is tied to the retrieved version."""
    mock_retriever = MagicMock(spec=PgRetriever)
    # Mock a specific version
    v_id = "version_123"
    mock_retriever.retrieve.return_value = [
        (MockChunk("T1", 0), MockVersion(2), MockDocument("Doc"), 0.9)
    ]
    
    mock_llm = MagicMock(spec=LLM)
    mock_llm.generate.return_value = ("Answer", "test-model")
    
    answerer = RAGAnswerer(mock_retriever, mock_llm)
    response = answerer.answer("Question", v_id)
    
    # Ensure retriever was called with the correct version_id
    mock_retriever.retrieve.assert_called_once_with(
        query="Question", top_k=3, version_id=v_id
    )
    # Ensure metadata matches the mocked version
    assert response.sources[0].version_number == 2

def test_context_budgeting_regression():
    """Test 6: Verify deterministic truncation and source synchronization."""
    mock_retriever = MagicMock(spec=PgRetriever)
    # 10 chunks, each quite large
    mock_retriever.retrieve.return_value = [
        (MockChunk("TEXT " + "A" * 1000, i), MockVersion(1), MockDocument("Doc"), 0.9 - (i*0.1))
        for i in range(10)
    ]
    
    mock_llm = MagicMock(spec=LLM)
    mock_llm.generate.return_value = ("Answer", "test-model")
    
    answerer = RAGAnswerer(mock_retriever, mock_llm)
    # Set a budget that allows only a few chunks
    answerer.MAX_CONTEXT_TOKENS = 1500
    
    response = answerer.answer("Question", "ver_1")
    
    # Verify chunks were removed from the end
    assert len(response.sources) < 10
    # The first chunk (most relevant) should still be there
    assert len(response.sources) > 0
    assert response.sources[0].text.startswith("TEXT")
    
    # Verify synchronization: the number of sources matches what was sent to the prompt
    args, kwargs = mock_llm.generate.call_args
    prompt_sent = args[0]
    
    import re
    markers = re.findall(r"\[Context (\d+)\]", prompt_sent)
    assert len(markers) == len(response.sources)
    # Ensure they are sequential from 1
    assert markers == [str(i+1) for i in range(len(response.sources))]
