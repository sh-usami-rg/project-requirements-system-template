# Project Requirements System - GitHub Integration

A comprehensive system for managing project requirements, tasks, schedules, and GitHub integration.

## Overview

This system provides:
- Structured task and schedule management using JSON files
- GitHub integration for issues, milestones, and projects
- Progress tracking and visualization
- Claude slash commands for easy automation
- Both Python and Bash implementation options

## Features

### Task Management
- Define tasks with priorities, effort estimates, and dependencies
- Organize tasks into milestones
- Track task status (pending, in_progress, completed)
- Assign tasks to team members

### GitHub Integration
- Automatically create and update GitHub Issues from tasks
- Sync milestones with GitHub Milestones
- Add appropriate labels for status and priority
- Track progress with GitHub Projects
- Close/reopen issues based on task status

### Progress Tracking
- Calculate task completion percentage
- Track effort progress in person-days
- Visualize progress on GitHub
- Generate progress reports

## Quick Start

### 1. Prerequisites

- Python 3.6+ or Bash
- GitHub CLI (`gh`) installed and authenticated
- Git repository connected to GitHub
- `jq` (for Bash version only)

### 2. Installation

```bash
# Install GitHub CLI
# macOS
brew install gh

# Linux (Ubuntu/Debian)
sudo apt install gh

# Authenticate
gh auth login

# For Bash version, also install jq
# macOS
brew install jq

# Linux (Ubuntu/Debian)
sudo apt install jq
```

See [docs/GITHUB_SETUP.md](docs/GITHUB_SETUP.md) for detailed installation instructions.

### 3. Basic Usage

#### Using Claude Slash Command

```
/github-sync
```

#### Using Python Script

```bash
python3 scripts/github-sync.py
```

#### Using Bash Script

```bash
./scripts/github-sync.sh
```

## File Structure

```
project-requirements-system/
├── README.md                   # Japanese README
├── README_EN.md                # This file (English README)
├── tasks.json                  # Task definitions
├── schedule.json               # Task schedule
├── .claude/
│   └── commands/
│       ├── github-sync.md      # GitHub sync command
│       └── spec-refine.md      # Spec refinement command
├── scripts/
│   ├── github-sync.py          # Python sync script
│   └── github-sync.sh          # Bash sync script
└── docs/
    └── GITHUB_SETUP.md         # Setup guide
```

## Data Format

### tasks.json

```json
{
  "project": {
    "name": "Project Name",
    "description": "Project description",
    "repository": "owner/repo",
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

### schedule.json

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

## Scripts

### Python Version (github-sync.py)

**Pros:**
- More robust error handling
- Better JSON parsing
- Cross-platform compatibility
- Easier to extend

**Usage:**
```bash
python3 scripts/github-sync.py [OPTIONS]

Options:
  --tasks PATH         Path to tasks.json (default: tasks.json)
  --schedule PATH      Path to schedule.json (default: schedule.json)
  --repo OWNER/REPO    GitHub repository (auto-detected if not specified)
```

### Bash Version (github-sync.sh)

**Pros:**
- No Python dependency
- Fast execution
- Native shell integration
- Requires `jq` for JSON parsing

**Usage:**
```bash
./scripts/github-sync.sh [OPTIONS]

Options:
  --tasks PATH         Path to tasks.json (default: tasks.json)
  --schedule PATH      Path to schedule.json (default: schedule.json)
  --repo OWNER/REPO    GitHub repository (auto-detected if not specified)
```

## Claude Slash Command

The `/github-sync` command provides an easy way to sync tasks with GitHub when using Claude Code.

**Location:** `.claude/commands/github-sync.md`

**Usage:** Simply type `/github-sync` in Claude Code

## Documentation

- [GitHub Setup Guide](docs/GITHUB_SETUP.md) - Detailed setup and configuration instructions
- [Task Schema](tasks.json) - Task definition format
- [Schedule Schema](schedule.json) - Schedule format

## Workflow

### 1. Initial Setup

1. Create or update `tasks.json` with your project tasks
2. Create or update `schedule.json` with task schedules
3. Run the sync script to create GitHub issues and milestones
4. Set up GitHub Project board for visual management

### 2. Ongoing Updates

1. Update task status in `tasks.json`
2. Run sync script to update GitHub
3. View progress on GitHub Issues, Milestones, and Projects

### 3. Progress Tracking

- Check progress summary in sync script output
- View milestone completion on GitHub Milestones page
- Use GitHub Project boards for visual kanban view
- Filter issues by labels, status, milestone

## Examples

### Create a New Task

Add to `tasks.json`:

```json
{
  "id": "T9",
  "title": "New Feature Implementation",
  "description": "Implement the new feature X",
  "assignee": "username",
  "status": "pending",
  "priority": "high",
  "effort_days": 8,
  "milestone": "M2",
  "dependencies": ["T6"],
  "labels": ["feature", "backend"]
}
```

Then run:
```bash
python3 scripts/github-sync.py
```

### Update Task Status

In `tasks.json`, change:
```json
"status": "pending"
```
to:
```json
"status": "in_progress"
```

Then run:
```bash
python3 scripts/github-sync.py
```

The corresponding GitHub issue will be updated automatically.

### Complete a Task

In `tasks.json`, change:
```json
"status": "in_progress"
```
to:
```json
"status": "completed"
```

Then run:
```bash
python3 scripts/github-sync.py
```

The GitHub issue will be automatically closed.

## Troubleshooting

### GitHub CLI Not Authenticated

```bash
gh auth login
```

### Repository Not Detected

Specify manually:
```bash
python3 scripts/github-sync.py --repo owner/repo
```

### Permission Denied

Ensure you have write access to the repository:
```bash
gh auth refresh -h github.com -s repo
```

### Duplicate Issues

Keep task IDs and titles consistent to avoid creating duplicate issues.

## Advanced Features

### Custom Labels

Add custom labels to tasks for better organization:
```json
"labels": ["frontend", "bug", "urgent"]
```

### Dependencies

Track task dependencies:
```json
"dependencies": ["T1", "T2"]
```

Dependencies are listed in issue descriptions.

### Assignees

Automatically assign issues:
```json
"assignee": "github_username"
```

### GitHub Actions Integration

Automate syncing with GitHub Actions:

`.github/workflows/sync.yml`:
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

## Best Practices

1. **Keep Task IDs Stable** - Don't change task IDs to avoid duplicate issues
2. **Regular Syncing** - Sync after significant changes to tasks
3. **Consistent Labels** - Use consistent label naming for filtering
4. **Realistic Estimates** - Provide realistic effort estimates
5. **Clear Dependencies** - Document task dependencies clearly
6. **Meaningful Descriptions** - Write clear, detailed task descriptions

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is provided as-is for project management purposes.

## Support

For issues and questions:
- Check [docs/GITHUB_SETUP.md](docs/GITHUB_SETUP.md)
- Review script output for error messages
- Ensure GitHub CLI is properly authenticated
- Verify JSON file formats are valid

## Resources

- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub Issues](https://docs.github.com/en/issues)
- [GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub Milestones](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/about-milestones)
