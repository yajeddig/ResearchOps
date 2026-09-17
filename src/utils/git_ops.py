"""
Safe git commit/push for GitHub Actions runners.

Design:
- Commit once, locally.
- Retry ONLY the `pull --rebase` + `push` pair. Retrying the whole function
  (previous behaviour) re-ran `git status`, saw a clean tree after the first
  commit, printed "Nothing to commit" and returned without ever pushing.
- Concurrent WF1 runs both append to data/history.json. A textual rebase
  conflict on that file is resolved automatically by merging the two JSON
  dictionaries (union of keys). Any other conflict aborts the rebase and
  the push is retried, then reported.
"""
import json
import os
import subprocess
import time

from utils.logger import get_logger

log = get_logger("GIT")

MERGEABLE_JSON_FILES = {"data/history.json"}


def run_cmd(cmd: list[str], check: bool = True, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run a command and capture its output."""
    log.debug(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0 and check:
        log.error(f"Command failed: {' '.join(cmd)}\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result


def _conflicted_files() -> list[str]:
    out = run_cmd(["git", "diff", "--name-only", "--diff-filter=U"], check=False).stdout
    return [line.strip() for line in out.splitlines() if line.strip()]


def _merge_json_stages(path: str) -> None:
    """
    During a rebase, stage 2 is the upstream version (already on the remote)
    and stage 3 is the version from the commit being replayed (ours).
    Both are flat JSON dicts keyed by hash: keep the union, ours wins on ties.
    """
    upstream = run_cmd(["git", "show", f":2:{path}"], check=False).stdout or "{}"
    ours = run_cmd(["git", "show", f":3:{path}"], check=False).stdout or "{}"
    try:
        merged = json.loads(upstream)
        merged.update(json.loads(ours))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Cannot merge {path}: invalid JSON in one side ({exc})") from exc
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(merged, indent=2, ensure_ascii=False))
    run_cmd(["git", "add", path])
    log.info(f"Auto-merged {path} ({len(merged)} entries)")


def _resolve_rebase_conflicts() -> bool:
    """Try to finish an interrupted rebase. Returns True on success."""
    conflicts = _conflicted_files()
    if not conflicts:
        return False
    for path in conflicts:
        if path in MERGEABLE_JSON_FILES:
            _merge_json_stages(path)
        else:
            log.error(f"Unmergeable conflict in {path}")
            return False
    env = dict(os.environ, GIT_EDITOR="true")
    result = run_cmd(["git", "rebase", "--continue"], check=False, env=env)
    return result.returncode == 0


def push_with_retry(attempts: int = 3, wait_seconds: float = 2.0) -> None:
    """Rebase on the remote then push; retried to absorb concurrent pushes."""
    last_error = ""
    for attempt in range(1, attempts + 1):
        pull = run_cmd(["git", "pull", "--rebase"], check=False)
        if pull.returncode != 0:
            if not _resolve_rebase_conflicts():
                run_cmd(["git", "rebase", "--abort"], check=False)
                last_error = f"pull --rebase failed: {pull.stderr.strip()[:300]}"
                log.warning(f"Push attempt {attempt}/{attempts}: {last_error}")
                time.sleep(wait_seconds)
                continue
        push = run_cmd(["git", "push"], check=False)
        if push.returncode == 0:
            log.info("Pushed successfully")
            return
        last_error = f"push failed: {push.stderr.strip()[:300]}"
        log.warning(f"Push attempt {attempt}/{attempts}: {last_error}")
        time.sleep(wait_seconds)
    raise RuntimeError(f"Git push failed after {attempts} attempts ({last_error})")


def safe_commit(files: list[str], message: str) -> bool:
    """
    Stage `files`, commit with `message`, then push with retry.
    Returns True if something was committed and pushed, False if nothing changed.
    """
    run_cmd(["git", "config", "user.name", "ResearchOps Bot"])
    run_cmd(["git", "config", "user.email", "bot@researchops.local"])

    for f in files:
        run_cmd(["git", "add", f])

    status = run_cmd(["git", "status", "--porcelain"], check=False)
    if not status.stdout.strip():
        log.info("Nothing to commit")
        return False

    run_cmd(["git", "commit", "-m", message])
    push_with_retry()
    return True
