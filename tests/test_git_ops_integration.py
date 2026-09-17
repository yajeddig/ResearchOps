"""
Integration tests for safe_commit against a real (temporary) git remote.

Reproduces the production failure: two WF1 runs push concurrently, both
append to data/history.json, the second one hits a rebase conflict.
"""
import json
import subprocess
from pathlib import Path

import pytest

from utils.git_ops import safe_commit


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)


@pytest.fixture
def repos(tmp_path):
    """A bare remote plus two clones (A = other runner, B = the one under test)."""
    remote = tmp_path / "remote.git"
    git("init", "--bare", "-q", "-b", "main", str(remote), cwd=tmp_path)

    seed = tmp_path / "seed"
    git("clone", "-q", str(remote), str(seed), cwd=tmp_path)
    git("config", "user.email", "seed@test", cwd=seed)
    git("config", "user.name", "seed", cwd=seed)
    (seed / "data").mkdir()
    (seed / "data" / "history.json").write_text(json.dumps({"base": {"url": "u0"}}, indent=2))
    git("add", ".", cwd=seed)
    git("commit", "-q", "-m", "seed", cwd=seed)
    git("push", "-q", "-u", "origin", "main", cwd=seed)

    a = tmp_path / "a"
    b = tmp_path / "b"
    git("clone", "-q", str(remote), str(a), cwd=tmp_path)
    git("clone", "-q", str(remote), str(b), cwd=tmp_path)
    for clone in (a, b):
        git("config", "user.email", "bot@test", cwd=clone)
        git("config", "user.name", "bot", cwd=clone)
    return remote, a, b


def _write_history(clone: Path, extra: dict):
    path = clone / "data" / "history.json"
    data = json.loads(path.read_text())
    data.update(extra)
    path.write_text(json.dumps(data, indent=2))


def _remote_history(remote: Path) -> dict:
    out = subprocess.run(["git", "show", "main:data/history.json"], cwd=remote, capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def test_push_without_contention(repos, monkeypatch):
    _, _, b = repos
    monkeypatch.chdir(b)
    (b / "card.md").write_text("card")
    _write_history(b, {"b1": {"url": "ub1"}})

    assert safe_commit(["card.md", "data/history.json"], "WF1: card") is True

    remote_history = _remote_history(repos[0])
    assert set(remote_history) == {"base", "b1"}


def test_concurrent_history_conflict_is_auto_merged(repos, monkeypatch):
    remote, a, b = repos

    # Runner A lands first with its own history entry
    (a / "card_a.md").write_text("A")
    _write_history(a, {"a1": {"url": "ua1"}})
    git("add", ".", cwd=a)
    git("commit", "-q", "-m", "WF1: A", cwd=a)
    git("push", "-q", cwd=a)

    # Runner B, unaware of A, commits a conflicting history.json
    monkeypatch.chdir(b)
    (b / "card_b.md").write_text("B")
    _write_history(b, {"b1": {"url": "ub1"}})

    assert safe_commit(["card_b.md", "data/history.json"], "WF1: B") is True

    remote_history = _remote_history(remote)
    assert set(remote_history) == {"base", "a1", "b1"}, "both runners' entries must survive"
    log = git("log", "--format=%s", "origin/main", cwd=b).stdout.split()
    assert "B" in log and "A" in log
    # Working tree is clean and no rebase is left dangling
    assert git("status", "--porcelain", cwd=b).stdout.strip() == ""
    assert not (b / ".git" / "rebase-merge").exists()


def test_unmergeable_conflict_raises_cleanly(repos, monkeypatch):
    remote, a, b = repos
    (a / "shared.md").write_text("version A")
    git("add", ".", cwd=a)
    git("commit", "-q", "-m", "A", cwd=a)
    git("push", "-q", cwd=a)

    monkeypatch.chdir(b)
    (b / "shared.md").write_text("version B")
    git("add", "shared.md", cwd=b)
    git("commit", "-q", "-m", "B", cwd=b)

    from utils import git_ops
    monkeypatch.setattr(git_ops.time, "sleep", lambda s: None)
    with pytest.raises(RuntimeError, match="Git push failed"):
        git_ops.push_with_retry(attempts=2)
    # Rebase aborted: repo usable, local commit preserved
    assert not (b / ".git" / "rebase-merge").exists()
    assert git("log", "-1", "--format=%s", cwd=b).stdout.strip() == "B"
