import pytest
from unittest.mock import MagicMock, patch
from app.generation.qa import RAGAnswerer
from app.generation.llm import LLM
from app.retrieval.pg_retriever import PgRetriever

def test_citation_mapping():
    # Mock retriever to return 2 chunks
    mock_retriever = MagicMock(spec=PgRetriever)
    mock_retriever.retrieve.return_value = [
        (MagicMock(text="Chunk 1", chunk_index=0), MagicMock(version_number=1), MagicMock(name="Doc 1"), 0.9),
        (MagicMock(text="Chunk 2", chunk_index=1), MagicMock(version_number=1), MagicMock(name="Doc 1"), 0.8),
    ]
    
    mock_llm = MagicMock(spec=LLM)
    mock_llm.generate.return_value = ("The answer is in [1] and [2].", "test-model")
    
    answerer = RAGAnswerer(mock_retriever, mock_llm)
    response = answerer.answer("Question", "ver_1")
    
    assert "answer" in response.__dict__
    # Verify sources match provided chunks
    assert len(response.sources) == 2
    assert response.sources[0].text == "Chunk 1"

def test_invalid_citations_logging(caplog):
    mock_retriever = MagicMock(spec=PgRetriever)
    mock_retriever.retrieve.return_value = [
        (MagicMock(text="Chunk 1", chunk_index=0), MagicMock(version_number=1), MagicMock(name="Doc 1"), 0.9),
    ]
    
    mock_llm = MagicMock(spec=LLM)
    mock_llm.generate.return_value = ("The answer is [1] and [99].", "test-model")
    
    answerer = RAGAnswerer(mock_retriever, mock_llm)
    answerer.answer("Question", "ver_1")
    
    assert "LLM invented citations: ['[99]']" in caplog.text

def test_token_overflow_handling():
    mock_retriever = MagicMock(spec=PgRetriever)
    # Provide a huge amount of text to trigger overflow
    # approx 4 chars per token. 8k limit.
    # 100 chunks of 1000 chars = 100k chars ~ 25k tokens.
    mock_retriever.retrieve.return_value = [
        (MagicMock(text="A" * 1000, chunk_index=i), MagicMock(version_number=1), MagicMock(name="Doc 1"), 0.9)
        for i in range(100)
    ]
    
    mock_llm = MagicMock(spec=LLM)
    mock_llm.generate.return_value = ("Answer", "test-model")
    
    answerer = RAGAnswerer(mock_retriever, mock_llm)
    # Set a very small budget to force truncation
    answerer.MAX_CONTEXT_TOKENS = 100
    
    response = answerer.answer("Question", "ver_1")
    
    # Should have truncated sources to fit the budget
    assert len(response.sources) < 100
    assert len(response.sources) >= 0

def test_empty_context_abstention():
    mock_retriever = MagicMock(spec=PgRetriever)
    mock_retriever.retrieve.return_value = []
    
    mock_llm = MagicMock(spec=LLM)
    
    answerer = RAGAnswerer(mock_retriever, mock_llm)
    response = answerer.answer("Question", "ver_1")
    
    assert "I don't have enough information" in response.answer
    assert mock_llm.generate.call_count == 0
