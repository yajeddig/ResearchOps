"""
Unit tests for WF3 Tri-Force Agents

Note: These tests verify agent structure and error handling.
API call mocking requires module reimport which is handled via importlib.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
import importlib


def reload_agent_module(module_name):
    """Helper to force module reload for clean mocking"""
    full_name = f"agents.{module_name}"
    if full_name in sys.modules:
        del sys.modules[full_name]
    return importlib.import_module(full_name)


class TestPerplexityAgent:
    """Tests for PerplexityAgent"""

    def test_agent_has_correct_model(self):
        """Test that agent uses sonar-pro model"""
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"}):
            with patch('openai.OpenAI'):
                module = reload_agent_module('perplexity_agent')
                agent = module.PerplexityAgent()
                assert agent.model == "sonar-pro"

    def test_agent_has_research_method(self):
        """Test that agent has callable research method"""
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"}):
            with patch('openai.OpenAI'):
                module = reload_agent_module('perplexity_agent')
                agent = module.PerplexityAgent()
                assert hasattr(agent, 'research')
                assert callable(agent.research)

    def test_research_returns_error_on_exception(self):
        """Test that research handles API errors gracefully"""
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"}):
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            with patch('openai.OpenAI', return_value=mock_client):
                module = reload_agent_module('perplexity_agent')
                agent = module.PerplexityAgent()
                result = agent.research("test query")
                assert "Error during Perplexity search" in result

    def test_research_success(self):
        """Test successful research returns content"""
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"}):
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(content="Research results"))]
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response

            with patch('openai.OpenAI', return_value=mock_client):
                module = reload_agent_module('perplexity_agent')
                agent = module.PerplexityAgent()
                result = agent.research("Digital Twin")
                assert result == "Research results"


class TestGeminiAgent:
    """Tests for GeminiAgent"""

    def test_agent_has_research_method(self):
        """Test that agent has callable research method"""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key", "TAVILY_API_KEY": "tavily-key"}):
            with patch('google.generativeai.configure'):
                with patch('google.generativeai.GenerativeModel'):
                    with patch('tavily.TavilyClient'):
                        module = reload_agent_module('gemini_agent')
                        agent = module.GeminiAgent()
                        assert hasattr(agent, 'research')
                        assert callable(agent.research)

    def test_research_handles_gemini_error(self):
        """Test that research handles Gemini API errors"""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key", "TAVILY_API_KEY": "tavily-key"}):
            mock_model = MagicMock()
            mock_model.generate_content.side_effect = Exception("Gemini Error")

            with patch('google.generativeai.configure'):
                with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                    with patch('tavily.TavilyClient') as mock_tavily:
                        mock_tavily.return_value.search.return_value = {'answer': '', 'results': []}
                        module = reload_agent_module('gemini_agent')
                        agent = module.GeminiAgent()
                        result = agent.research("Test query")
                        assert "Error during Gemini analysis" in result

    def test_research_continues_on_tavily_failure(self):
        """Test that research continues even if Tavily fails"""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key", "TAVILY_API_KEY": "tavily-key"}):
            mock_model = MagicMock()
            mock_model.generate_content.return_value = MagicMock(text="Fallback result")

            mock_tavily = MagicMock()
            mock_tavily.search.side_effect = Exception("Tavily down")

            with patch('google.generativeai.configure'):
                with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                    with patch('tavily.TavilyClient', return_value=mock_tavily):
                        module = reload_agent_module('gemini_agent')
                        agent = module.GeminiAgent()
                        result = agent.research("Test query")
                        assert result == "Fallback result"


class TestClaudeAgent:
    """Tests for ClaudeAgent"""

    def test_agent_has_correct_model(self):
        """Test that agent uses Claude Opus model"""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch('anthropic.Anthropic'):
                module = reload_agent_module('claude_agent')
                agent = module.ClaudeAgent()
                assert agent.model == "claude-3-opus-20240229"

    def test_agent_has_synthesize_method(self):
        """Test that agent has callable synthesize method"""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch('anthropic.Anthropic'):
                module = reload_agent_module('claude_agent')
                agent = module.ClaudeAgent()
                assert hasattr(agent, 'synthesize')
                assert callable(agent.synthesize)

    def test_synthesize_handles_error(self):
        """Test that synthesize handles API errors"""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            mock_client = MagicMock()
            mock_client.messages.create.side_effect = Exception("Claude Error")

            with patch('anthropic.Anthropic', return_value=mock_client):
                module = reload_agent_module('claude_agent')
                agent = module.ClaudeAgent()
                result = agent.synthesize("query", "context", "report1", "report2")
                assert "Error during Claude synthesis" in result

    def test_synthesize_success(self):
        """Test successful synthesis returns content"""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="# Master Report")]
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response

            with patch('anthropic.Anthropic', return_value=mock_client):
                module = reload_agent_module('claude_agent')
                agent = module.ClaudeAgent()
                result = agent.synthesize("query", "context", "report1", "report2")
                assert "Master Report" in result
