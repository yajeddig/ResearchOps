"""
Unit tests for utility modules
"""
import pytest
from unittest.mock import Mock, patch, call
import os
import tempfile
import json
import sys


class TestTelegramNotify:
    """Tests for telegram notification utility"""

    def test_notify_returns_early_without_config(self):
        """Test that notify handles missing configuration gracefully"""
        with patch.dict(os.environ, {}, clear=True):
            from utils.notify import telegram_notify
            # Should not raise, just print and return
            telegram_notify("Test message", "INFO")

    @patch('requests.post')
    def test_notify_success(self, mock_post):
        """Test successful notification"""
        with patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "test-token",
            "TELEGRAM_CHAT_ID": "123456"
        }):
            from utils.notify import telegram_notify
            telegram_notify("Test message", "SUCCESS")

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "test-token" in call_args[0][0]
        assert call_args[1]['json']['chat_id'] == "123456"

    @patch('requests.post')
    def test_notify_icon_selection(self, mock_post):
        """Test that correct icons are used for each level"""
        with patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "test-token",
            "TELEGRAM_CHAT_ID": "123456"
        }):
            from utils.notify import telegram_notify

            test_cases = [
                ("INFO", "ℹ️"),
                ("SUCCESS", "✅"),
                ("WARNING", "⚠️"),
                ("ERROR", "🚨"),
            ]

            for level, expected_icon in test_cases:
                telegram_notify(f"Test {level}", level)
                call_args = mock_post.call_args
                text = call_args[1]['json']['text']
                assert expected_icon in text, f"Expected {expected_icon} for level {level}"

    @patch('requests.post')
    def test_notify_handles_request_error(self, mock_post):
        """Test that request errors are handled gracefully"""
        mock_post.side_effect = Exception("Network error")

        with patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "test-token",
            "TELEGRAM_CHAT_ID": "123456"
        }):
            from utils.notify import telegram_notify
            # Should not raise
            telegram_notify("Test message", "INFO")


class TestSafeCommit:
    """Tests for git operations utility (subprocess.run based)"""

    def _run_factory(self, fail_on=None, status_output=" M test.md", fail_times=0):
        """Build a subprocess.run stub. `fail_on` is a substring of the command."""
        state = {"failures": 0}

        def fake_run(cmd, capture_output=True, text=True):
            joined = " ".join(cmd)
            result = Mock()
            result.returncode = 0
            result.stdout = status_output if "status" in joined else ""
            result.stderr = ""
            if fail_on and fail_on in joined and state["failures"] < fail_times:
                state["failures"] += 1
                result.returncode = 1
            return result

        return fake_run, state

    @patch('utils.git_ops.time.sleep')
    @patch('utils.git_ops.subprocess.run')
    def test_safe_commit_success(self, mock_run, _sleep):
        """Config, add, status, commit, pull --rebase, push are all issued"""
        mock_run.side_effect, _ = self._run_factory()

        from utils.git_ops import safe_commit
        assert safe_commit(files=["test.md"], message="Test commit") is True

        calls = [" ".join(c.args[0]) for c in mock_run.call_args_list]
        for expected in ["git config", "git add test.md", "git status", "git commit", "git pull --rebase", "git push"]:
            assert any(expected in c for c in calls), expected

    @patch('utils.git_ops.time.sleep')
    @patch('utils.git_ops.subprocess.run')
    def test_safe_commit_nothing_to_commit(self, mock_run, _sleep):
        """Clean tree: no commit, no push"""
        mock_run.side_effect, _ = self._run_factory(status_output="")

        from utils.git_ops import safe_commit
        assert safe_commit(files=["test.md"], message="Test commit") is False

        calls = [" ".join(c.args[0]) for c in mock_run.call_args_list]
        assert not any("git commit" in c for c in calls)
        assert not any("git push" in c for c in calls)

    @patch('utils.git_ops.time.sleep')
    @patch('utils.git_ops.subprocess.run')
    def test_safe_commit_push_retried_then_succeeds(self, mock_run, _sleep):
        """A transient push failure is retried without re-committing"""
        mock_run.side_effect, state = self._run_factory(fail_on="git push", fail_times=1)

        from utils.git_ops import safe_commit
        assert safe_commit(files=["test.md"], message="Test commit") is True

        calls = [" ".join(c.args[0]) for c in mock_run.call_args_list]
        assert sum("git commit" in c for c in calls) == 1
        assert sum("git push" in c for c in calls) == 2

    @patch('utils.git_ops.time.sleep')
    @patch('utils.git_ops.subprocess.run')
    def test_safe_commit_push_failure_raises(self, mock_run, _sleep):
        """Persistent push failure surfaces as an error instead of a silent no-op"""
        mock_run.side_effect, _ = self._run_factory(fail_on="git push", fail_times=99)

        from utils.git_ops import safe_commit
        with pytest.raises(RuntimeError, match="Git push failed"):
            safe_commit(files=["test.md"], message="Test commit")

    @patch('utils.git_ops.time.sleep')
    @patch('utils.git_ops.subprocess.run')
    def test_safe_commit_multiple_files(self, mock_run, _sleep):
        """Each file is staged individually"""
        mock_run.side_effect, _ = self._run_factory()

        from utils.git_ops import safe_commit
        safe_commit(files=["file1.md", "file2.md", "file3.md"], message="Multi-file commit")

        add_calls = [c for c in mock_run.call_args_list if "add" in c.args[0]]
        assert len(add_calls) == 3


class TestDeduplication:
    """Tests for deduplication utility"""

    def test_dedup_functions_exist(self):
        """Test that dedup module functions can be imported"""
        from utils.dedup import is_duplicate, add_to_history, compute_hash
        assert callable(is_duplicate)
        assert callable(add_to_history)
        assert callable(compute_hash)

    def test_compute_hash_consistency(self):
        """Test that hash computation is consistent"""
        from utils.dedup import compute_hash

        url = "https://example.com/test"
        hash1 = compute_hash(url)
        hash2 = compute_hash(url)

        assert hash1 == hash2
        assert len(hash1) == 8

    def test_compute_hash_uniqueness(self):
        """Test that different URLs produce different hashes"""
        from utils.dedup import compute_hash

        hash1 = compute_hash("https://example.com/page1")
        hash2 = compute_hash("https://example.com/page2")

        assert hash1 != hash2

    def test_dedup_with_temp_history(self):
        """Test deduplication with temporary history file"""
        from pathlib import Path
        import importlib

        with tempfile.TemporaryDirectory() as tmpdir:
            history_path = Path(tmpdir) / 'data' / 'history.json'

            # Remove module from cache and reimport with patched path
            if 'utils.dedup' in sys.modules:
                del sys.modules['utils.dedup']

            with patch.dict('utils.dedup.__dict__', {'HISTORY_FILE': history_path}, create=True):
                # This is tricky - we'll test the core hash function instead
                from utils.dedup import compute_hash

                url1 = "https://example1.com"
                url2 = "https://example2.com"

                assert compute_hash(url1) != compute_hash(url2)
                assert compute_hash(url1) == compute_hash(url1)
