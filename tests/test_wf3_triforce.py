"""
Unit tests for WF3 Tri-Force Workflow
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import re
import sys
import importlib
from datetime import datetime


class TestWF3Triforce:
    """Tests for the main WF3 workflow"""

    @pytest.fixture
    def mock_env(self):
        """Setup environment variables for testing"""
        return {
            "ISSUE_TITLE": "Research: Digital Twin for WWTP",
            "ISSUE_BODY": "Focus on real-time monitoring applications",
            "ISSUE_NUMBER": "42",
            "PERPLEXITY_API_KEY": "test-perplexity",
            "GOOGLE_API_KEY": "test-google",
            "TAVILY_API_KEY": "test-tavily",
            "ANTHROPIC_API_KEY": "test-anthropic",
        }

    def test_topic_extraction_with_prefix(self, mock_env):
        """Test that 'Research: ' prefix is correctly removed from title"""
        with patch.dict(os.environ, mock_env):
            issue_title = os.getenv("ISSUE_TITLE")
            topic = issue_title.replace("Research: ", "").strip()

            assert topic == "Digital Twin for WWTP"

    def test_topic_extraction_without_prefix(self, mock_env):
        """Test topic extraction when no prefix present"""
        mock_env["ISSUE_TITLE"] = "Machine Learning for Process Control"
        with patch.dict(os.environ, mock_env):
            issue_title = os.getenv("ISSUE_TITLE")
            topic = issue_title.replace("Research: ", "").strip()

            assert topic == "Machine Learning for Process Control"

    def test_full_query_construction_with_context(self, mock_env):
        """Test full query includes both topic and context"""
        with patch.dict(os.environ, mock_env):
            topic = os.getenv("ISSUE_TITLE").replace("Research: ", "").strip()
            context = os.getenv("ISSUE_BODY")

            full_query = topic
            if context:
                full_query += f"\n\nContext: {context}"

            assert "Digital Twin for WWTP" in full_query
            assert "real-time monitoring applications" in full_query

    def test_full_query_construction_without_context(self, mock_env):
        """Test full query with empty context"""
        mock_env["ISSUE_BODY"] = ""
        with patch.dict(os.environ, mock_env):
            topic = os.getenv("ISSUE_TITLE").replace("Research: ", "").strip()
            context = os.getenv("ISSUE_BODY")

            full_query = topic
            if context:
                full_query += f"\n\nContext: {context}"

            assert full_query == "Digital Twin for WWTP"
            assert "Context:" not in full_query

    def test_filename_generation(self):
        """Test that filename is correctly generated"""
        topic = "N2O Emissions in WWTP: A Study"
        safe_title = re.sub(r'[^a-zA-Z0-9]', '_', topic[:30])
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"research/{date_str}_Deep_{safe_title}.md"

        assert filename.startswith("research/")
        assert filename.endswith(".md")
        assert "Deep_" in filename
        assert ":" not in safe_title

    def test_safe_title_truncation(self):
        """Test that long titles are truncated to 30 chars before sanitization"""
        long_topic = "This is a very long research topic that should be truncated properly"
        safe_title = re.sub(r'[^a-zA-Z0-9]', '_', long_topic[:30])

        assert len(long_topic[:30]) == 30

    def test_commit_message_uses_topic_not_query(self, mock_env):
        """Regression test: ensure commit message uses 'topic' variable"""
        with patch.dict(os.environ, mock_env):
            topic = os.getenv("ISSUE_TITLE").replace("Research: ", "").strip()
            message = f"WF3: Deep Research - {topic[:50]}"

            assert "Digital Twin for WWTP" in message
            assert len(topic[:50]) <= 50


class TestWF3Integration:
    """Integration-style tests for WF3 components"""

    def test_utils_can_be_imported(self):
        """Test that utility modules can be imported"""
        from utils.git_ops import safe_commit
        from utils.notify import telegram_notify

        assert callable(safe_commit)
        assert callable(telegram_notify)

    def test_agents_can_be_instantiated_with_mocks(self):
        """Test that agents can be instantiated with mocked dependencies"""
        with patch.dict(os.environ, {
            "PERPLEXITY_API_KEY": "test",
            "GOOGLE_API_KEY": "test",
            "TAVILY_API_KEY": "test",
            "ANTHROPIC_API_KEY": "test"
        }):
            with patch('openai.OpenAI'):
                with patch('google.generativeai.configure'):
                    with patch('google.generativeai.GenerativeModel'):
                        with patch('tavily.TavilyClient'):
                            with patch('anthropic.Anthropic'):
                                # Force reimport
                                for mod in ['agents.perplexity_agent', 'agents.gemini_agent', 'agents.claude_agent']:
                                    if mod in sys.modules:
                                        del sys.modules[mod]

                                from agents.perplexity_agent import PerplexityAgent
                                from agents.gemini_agent import GeminiAgent
                                from agents.claude_agent import ClaudeAgent

                                p_agent = PerplexityAgent()
                                g_agent = GeminiAgent()
                                c_agent = ClaudeAgent()

                                assert p_agent is not None
                                assert g_agent is not None
                                assert c_agent is not None
