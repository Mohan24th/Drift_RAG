import pytest
from unittest.mock import MagicMock, patch
from app.generation.llm import LLM
from groq import APIError, RateLimitError

def test_primary_success():
    llm = LLM(model="primary", fallback_model="fallback")
    with patch.object(llm, '_call_model', return_value="Correct Answer") as mock_call:
        assert llm.generate("Hello") == ("Correct Answer", "primary")
        mock_call.assert_called_once_with("Hello", "primary")

def test_primary_transient_fallback_success():
    llm = LLM(model="primary", fallback_model="fallback")
    with patch.object(llm, '_call_model') as mock_call:
        # Use a generic exception that we can manually cast or 
        # just use a custom class that inherits from APIError without calling super()
        class MockAPIError(APIError):
            def __init__(self, message):
                self.message = message
                # Do not call super().__init__ to avoid the request requirement
        
        mock_call.side_effect = [MockAPIError("Server Error"), "Fallback Answer"]
        assert llm.generate("Hello") == ("Fallback Answer", "fallback")
        assert mock_call.call_count == 2
        mock_call.assert_any_call("Hello", "primary")
        mock_call.assert_any_call("Hello", "fallback")

def test_primary_permanent_no_fallback():
    llm = LLM(model="primary", fallback_model="fallback")
    with patch.object(llm, '_call_model') as mock_call:
        mock_call.side_effect = ValueError("Empty response")
        with pytest.raises(ValueError, match="Empty response"):
            llm.generate("Hello")
        assert mock_call.call_count == 1

def test_both_models_fail():
    llm = LLM(model="primary", fallback_model="fallback")
    with patch.object(llm, '_call_model') as mock_call:
        class MockAPIError(APIError):
            def __init__(self, message):
                self.message = message
        
        mock_call.side_effect = [MockAPIError("Error 1"), MockAPIError("Error 2")]
        with pytest.raises(RuntimeError, match="Both primary and fallback LLM requests failed"):
            llm.generate("Hello")
        assert mock_call.call_count == 2

def test_timeout_config():
    from app.config import settings
    llm = LLM()
    assert llm.client.timeout == settings.llm_timeout
