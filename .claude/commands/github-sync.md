---
description: Sync tasks.json and schedule.json with GitHub Issues, Projects, and Milestones
---

# GitHub Sync Command

Please execute the GitHub synchronization script to sync tasks.json and schedule.json with GitHub.

## Instructions

1. Run the GitHub sync script:
   ```bash
   python3 scripts/github-sync.py --tasks tasks.json --schedule schedule.json
   ```

2. The script will:
   - Auto-detect the GitHub repository from git remote
   - Create or update GitHub Milestones from tasks.json
   - Create or update GitHub Issues for each task
   - Add appropriate labels (status, priority)
   - Link issues to milestones
   - Close issues that are marked as completed
   - Display progress statistics

3. After syncing, provide a summary of:
   - Number of milestones created/updated
   - Number of issues created/updated
   - Overall progress percentage
   - Links to view issues and milestones on GitHub

4. If the script encounters any errors, provide troubleshooting steps.

## Optional Parameters

- `--repo OWNER/REPO`: Specify GitHub repository manually (if auto-detection fails)
- `--tasks PATH`: Specify custom path to tasks.json
- `--schedule PATH`: Specify custom path to schedule.json

## Example Output

The script should display:
- Authentication status
- Loaded task count
- Created/updated milestones
- Created/updated issues
- Progress summary with percentages
- Links to GitHub pages

## Notes

- Ensure gh CLI is installed and authenticated before running
- The script requires write access to the repository
- Issues are matched by title (Task ID + Title)
- Existing issues will be updated, not duplicated
