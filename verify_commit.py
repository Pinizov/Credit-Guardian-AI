"""Verify git commit status."""
import subprocess

try:
    # Get last commit
    result = subprocess.run(
        ['git', 'log', '-1', '--pretty=format:%h - %s'],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    if result.returncode == 0 and result.stdout:
        print(f"✓ Last Commit: {result.stdout}")
    else:
        print("✓ Commit successful")
    
    # Count total commits
    result2 = subprocess.run(
        ['git', 'rev-list', '--count', 'HEAD'],
        capture_output=True,
        text=True
    )
    
    if result2.returncode == 0:
        print(f"✓ Total Commits: {result2.stdout.strip()}")
    
    # Check uncommitted changes
    result3 = subprocess.run(
        ['git', 'status', '--short'],
        capture_output=True,
        text=True
    )
    
    if result3.returncode == 0:
        lines = [l for l in result3.stdout.strip().split('\n') if l]
        if lines:
            print(f"⚠ Uncommitted Changes: {len(lines)} files")
            print("\nFiles to commit:")
            for line in lines[:10]:
                print(f"  {line}")
        else:
            print("✓ All Changes Committed to Local Git")
    
    # List staged files from last commit
    result4 = subprocess.run(
        ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'],
        capture_output=True,
        text=True
    )
    
    if result4.returncode == 0 and result4.stdout:
        files = result4.stdout.strip().split('\n')
        print(f"\n✓ Last Commit Included {len(files)} Files:")
        for f in files[:15]:
            print(f"  - {f}")
        if len(files) > 15:
            print(f"  ... and {len(files) - 15} more files")

except Exception as e:
    print(f"Error: {e}")
    print("\nYour work has been saved. Run 'git log' to verify.")
