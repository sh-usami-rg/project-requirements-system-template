# GitHub Integration Setup Guide

This guide explains how to set up and use the GitHub integration for syncing tasks.json and schedule.json with GitHub Issues, Projects, and Milestones.

## Overview

The GitHub sync system provides:
- Automatic creation and updating of GitHub Issues from tasks.json
- Milestone management synchronized with your project phases
- Progress tracking with labels and status
- Integration with GitHub Projects for visual task management
- Bi-directional sync capabilities

## Prerequisites

1. A GitHub account with access to a repository
2. Git repository initialized and connected to GitHub
3. GitHub CLI (gh) installed on your system
4. Python 3.6 or higher

## Installation

### 1. Install GitHub CLI

#### macOS
```bash
brew install gh
```

#### Linux (Debian/Ubuntu)
```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

#### Linux (Fedora/CentOS/RHEL)
```bash
sudo dnf install gh
```

#### Windows
```bash
winget install --id GitHub.cli
```

Or download from: https://cli.github.com/

### 2. Authenticate GitHub CLI

Run the following command and follow the prompts:

```bash
gh auth login
```

Choose:
- GitHub.com
- HTTPS or SSH (your preference)
- Authenticate with your browser or paste an authentication token

Verify authentication:
```bash
gh auth status
```

You should see a message indicating you're logged in.

### 3. Set Up Git Remote

If you haven't already, connect your local repository to GitHub:

```bash
# Create a new repository on GitHub first, then:
git remote add origin https://github.com/USERNAME/REPO_NAME.git

# Or for SSH:
git remote add origin git@github.com:USERNAME/REPO_NAME.git

# Verify:
git remote -v
```

## File Structure

```
project-requirements-system/
├── tasks.json              # Task definitions
├── schedule.json           # Task schedule
├── scripts/
│   └── github-sync.py      # Sync script
├── .claude/
│   └── commands/
│       └── github-sync.md  # Claude slash command
└── docs/
    └── GITHUB_SETUP.md     # This file
```

## Usage

### Method 1: Using Claude Slash Command

If you're using Claude Code, simply run:

```
/github-sync
```

This will execute the sync script and provide you with a summary.

### Method 2: Direct Script Execution

From the project root directory:

```bash
# Auto-detect repository from git remote
python3 scripts/github-sync.py

# Specify repository manually
python3 scripts/github-sync.py --repo USERNAME/REPO_NAME

# Use custom file paths
python3 scripts/github-sync.py --tasks path/to/tasks.json --schedule path/to/schedule.json
```

### Script Options

- `--tasks PATH`: Path to tasks.json (default: tasks.json)
- `--schedule PATH`: Path to schedule.json (default: schedule.json)
- `--repo OWNER/REPO`: GitHub repository (auto-detected if not specified)

## What Gets Synced

### Milestones

Each milestone in tasks.json is created as a GitHub Milestone with:
- Title
- Description
- Due date
- Associated tasks

### Issues

Each task in tasks.json is created as a GitHub Issue with:
- Title: `{task_id}: {task_title}`
- Description with task details
- Labels:
  - `status:{status}` (pending/in_progress/completed)
  - `priority:{priority}` (low/medium/high)
  - Custom labels from tasks.json
- Milestone assignment
- Assignee (if specified)
- Closed state (if status is "completed")

### Issue Body

Each issue includes:
- Task description
- Task ID
- Status
- Priority
- Effort estimation
- Milestone
- Dependencies
- Schedule (start/end dates from schedule.json)

## GitHub Projects Integration

### Manual Setup (Recommended for Projects V2)

1. Go to your repository on GitHub
2. Click on "Projects" tab
3. Click "New project"
4. Choose a template or start from scratch
5. Add a "Status" field with values: Pending, In Progress, Completed
6. Add your issues to the project

### Automatic Updates

The sync script will:
- Update issue status based on tasks.json
- Close completed issues
- Reopen issues if status changes from completed to in_progress/pending

## Workflow

### Initial Sync

1. Create or update your tasks.json and schedule.json
2. Run the sync script:
   ```bash
   python3 scripts/github-sync.py
   ```
3. Visit your GitHub repository to see:
   - Issues: `https://github.com/USERNAME/REPO/issues`
   - Milestones: `https://github.com/USERNAME/REPO/milestones`
   - Projects: `https://github.com/USERNAME/REPO/projects`

### Ongoing Sync

1. Update tasks.json locally (change status, add tasks, etc.)
2. Run the sync script again
3. Existing issues are updated, new ones are created
4. Completed tasks have their issues closed

## Progress Tracking

The sync script displays progress statistics:

```
=== Progress Summary ===
Repository: username/repo
Total Tasks: 8
  - Completed: 1
  - In Progress: 1
  - Pending: 6
Task Progress: 12.5%
Effort Progress: 8.1% (3/37 days)
```

You can also view progress on GitHub:
- Milestones page shows completion percentage
- Project boards provide visual kanban view
- Issues can be filtered by label, milestone, status

## Troubleshooting

### gh CLI not found

**Error**: `GitHub CLI (gh) is not installed`

**Solution**: Install gh CLI following the installation instructions above.

### Not authenticated

**Error**: `GitHub CLI is not authenticated`

**Solution**: Run `gh auth login` and follow the prompts.

### Repository not detected

**Error**: `Not in a git repository or no remote configured`

**Solution**:
- Ensure you're in the correct directory
- Add a git remote: `git remote add origin https://github.com/USERNAME/REPO.git`
- Or specify repository manually: `--repo USERNAME/REPO`

### Permission denied

**Error**: `Resource not accessible by integration`

**Solution**:
- Ensure you have write access to the repository
- Re-authenticate: `gh auth refresh -h github.com -s repo`

### Duplicate issues

**Issue**: Issues are being created multiple times

**Solution**:
- Issues are matched by title (Task ID + Title)
- If you changed task titles, the script will create new issues
- Manually close duplicate issues or keep task titles consistent

## Best Practices

1. **Consistent Task IDs**: Keep task IDs stable to avoid duplicate issues
2. **Regular Sync**: Run sync after significant changes to tasks.json
3. **Label Strategy**: Use consistent labels for filtering and organization
4. **Milestone Planning**: Plan milestones with realistic due dates
5. **Assignee Management**: Specify assignees in tasks.json for automatic assignment
6. **Project Boards**: Set up GitHub Project boards for visual management

## Advanced Usage

### Custom Labels

Add custom labels to tasks in tasks.json:

```json
{
  "id": "T1",
  "title": "Task Title",
  "labels": ["frontend", "bug", "priority:high"]
}
```

### Dependencies Tracking

Dependencies are listed in issue descriptions but not automatically linked. To link dependent issues:

1. Manual linking in issue comments
2. Use GitHub Actions for automation
3. Use task list checkboxes in issue descriptions

### Automation with GitHub Actions

Create `.github/workflows/sync.yml`:

```yaml
name: Sync Tasks

on:
  push:
    paths:
      - 'tasks.json'
      - 'schedule.json'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Sync with GitHub
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          python3 scripts/github-sync.py
```

## Data Format Reference

### tasks.json Structure

```json
{
  "project": {
    "name": "Project Name",
    "description": "Description",
    "repository": "username/repo",
    "start_date": "2026-01-15"
  },
  "milestones": [
    {
      "id": "M1",
      "title": "Milestone Title",
      "description": "Description",
      "due_date": "2026-02-15",
      "tasks": ["T1", "T2"]
    }
  ],
  "tasks": [
    {
      "id": "T1",
      "title": "Task Title",
      "description": "Task description",
      "assignee": "github_username",
      "status": "pending|in_progress|completed",
      "priority": "low|medium|high",
      "effort_days": 5,
      "milestone": "M1",
      "dependencies": ["T0"],
      "labels": ["label1", "label2"]
    }
  ]
}
```

### schedule.json Structure

```json
{
  "project": {
    "name": "Project Name",
    "start_date": "2026-01-15",
    "end_date": "2026-04-30"
  },
  "schedule": [
    {
      "task_id": "T1",
      "title": "Task Title",
      "start_date": "2026-01-15",
      "end_date": "2026-01-22",
      "effort_days": 5,
      "status": "pending",
      "assignee": "github_username"
    }
  ]
}
```

## Support and Resources

- GitHub CLI Documentation: https://cli.github.com/manual/
- GitHub Issues Documentation: https://docs.github.com/en/issues
- GitHub Projects Documentation: https://docs.github.com/en/issues/planning-and-tracking-with-projects
- GitHub Milestones: https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/about-milestones

## Contributing

To improve the GitHub sync functionality:

1. Fork the repository
2. Make your changes to `scripts/github-sync.py`
3. Test thoroughly
4. Submit a pull request

## License

This integration script is part of the project-requirements-system and follows the same license as the main project.
