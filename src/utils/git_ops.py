import subprocess
from tenacity import retry, stop_after_attempt, wait_fixed


def run_cmd(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run command with proper error capture."""
    print(f"🔧 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and check:
        print(f"❌ STDOUT: {result.stdout}")
        print(f"❌ STDERR: {result.stderr}")
        raise Exception(f"Command failed: {' '.join(cmd)}")
    return result


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def safe_commit(files, message):
    """
    Commits files with retry logic to handle race conditions.
    Uses subprocess for better error visibility.
    """
    # Configure git
    run_cmd(["git", "config", "user.name", "ResearchOps Bot"])
    run_cmd(["git", "config", "user.email", "bot@researchops.local"])

    # Pull latest changes to avoid conflicts
    run_cmd(["git", "pull", "--rebase"])

    # Add files
    for f in files:
        run_cmd(["git", "add", f])

    # Check if there are changes to commit
    status = run_cmd(["git", "status", "--porcelain"], check=False)
    if not status.stdout.strip():
        print("ℹ️ Nothing to commit")
        return

    # Commit
    run_cmd(["git", "commit", "-m", message])

    # Push
    run_cmd(["git", "push"])
    print("✅ Pushed successfully")
