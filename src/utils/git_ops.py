import os
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def safe_commit(files, message):
    """
    Commits files with retry logic to handle race conditions
    """
    # Configure git if needed (usually done by actions/checkout but good to be safe)
    os.system('git config user.name "ResearchOps Bot"')
    os.system('git config user.email "bot@researchops.local"')
    
    # Pull latest changes to avoid conflicts
    if os.system("git pull --rebase") != 0:
        raise Exception("Git pull failed")
    
    # Add files
    for f in files:
        if os.system(f'git add "{f}"') != 0:
             raise Exception(f"Git add failed for {f}")
    
    # Commit
    if os.system(f'git commit -m "{message}"') != 0:
        # Check if there are changes to commit
        status = os.popen("git status --porcelain").read()
        if not status:
            print("Nothing to commit")
            return
        raise Exception("Git commit failed")
    
    # Push
    if os.system("git push") != 0:
        raise Exception("Git push failed")
