"""
Safe git commit/push for GitHub Actions runners.

Design:
- Commit once, locally.
- Retry ONLY the `pull --rebase` + `push` pair. Retrying the whole function
  (previous behaviour) re-ran `git status`, saw a clean tree after the first
  commit, printed "Nothing to commit" and returned without ever pushing.
"""
import subprocess
import time

from utils.logger import get_logger

log = get_logger("GIT")


def run_cmd(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and capture its output."""
    log.debug(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and check:
        log.error(f"Command failed: {' '.join(cmd)}\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result


def push_with_retry(attempts: int = 3, wait_seconds: float = 2.0) -> None:
    """Rebase on the remote then push; retried to absorb concurrent pushes."""
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            run_cmd(["git", "pull", "--rebase"])
            run_cmd(["git", "push"])
            log.info("Pushed successfully")
            return
        except RuntimeError as exc:
            last_error = exc
            log.warning(f"Push attempt {attempt}/{attempts} failed")
            if attempt < attempts:
                time.sleep(wait_seconds)
    raise RuntimeError(f"Git push failed after {attempts} attempts") from last_error


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
