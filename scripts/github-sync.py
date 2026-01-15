#!/usr/bin/env python3
"""
GitHub Sync Script
Synchronizes tasks.json with GitHub Issues, Projects, and Milestones
"""

import json
import subprocess
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional


class GitHubSync:
    def __init__(self, tasks_file: str, schedule_file: str, repo: Optional[str] = None):
        """Initialize GitHub Sync

        Args:
            tasks_file: Path to tasks.json
            schedule_file: Path to schedule.json
            repo: GitHub repository (owner/repo). If None, auto-detect from git remote
        """
        self.tasks_file = tasks_file
        self.schedule_file = schedule_file
        self.repo = repo or self._detect_repo()
        self.tasks_data = None
        self.schedule_data = None

    def _detect_repo(self) -> str:
        """Auto-detect GitHub repository from git remote"""
        try:
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True,
                check=True
            )
            remote_url = result.stdout.strip()

            # Parse GitHub URL (supports both HTTPS and SSH)
            if 'github.com' in remote_url:
                if remote_url.startswith('git@github.com:'):
                    repo = remote_url.replace('git@github.com:', '').replace('.git', '')
                elif 'github.com/' in remote_url:
                    repo = remote_url.split('github.com/')[-1].replace('.git', '')
                else:
                    raise ValueError("Unable to parse GitHub URL")
                return repo
            else:
                raise ValueError("Not a GitHub repository")
        except subprocess.CalledProcessError:
            raise ValueError("Not in a git repository or no remote configured")

    def load_data(self):
        """Load tasks.json and schedule.json"""
        with open(self.tasks_file, 'r', encoding='utf-8') as f:
            self.tasks_data = json.load(f)

        with open(self.schedule_file, 'r', encoding='utf-8') as f:
            self.schedule_data = json.load(f)

        print(f"✓ Loaded {len(self.tasks_data['tasks'])} tasks from {self.tasks_file}")
        print(f"✓ Loaded {len(self.schedule_data['schedule'])} scheduled items from {self.schedule_file}")

    def _run_gh_command(self, args: List[str]) -> str:
        """Run gh CLI command"""
        try:
            result = subprocess.run(
                ['gh'] + args,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error running gh command: {e.stderr}")
            raise

    def check_gh_cli(self) -> bool:
        """Check if gh CLI is installed and authenticated"""
        try:
            result = subprocess.run(
                ['gh', 'auth', 'status'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✓ GitHub CLI is authenticated")
                return True
            else:
                print("✗ GitHub CLI is not authenticated")
                print("Please run: gh auth login")
                return False
        except FileNotFoundError:
            print("✗ GitHub CLI (gh) is not installed")
            print("Please install gh CLI: https://cli.github.com/")
            return False

    def create_or_update_milestones(self):
        """Create or update GitHub milestones"""
        print("\n=== Creating/Updating Milestones ===")

        # Get existing milestones
        existing_milestones = {}
        try:
            output = self._run_gh_command([
                'api', f'/repos/{self.repo}/milestones',
                '--jq', '.[] | {title: .title, number: .number}'
            ])
            for line in output.split('\n'):
                if line.strip():
                    data = json.loads(line)
                    existing_milestones[data['title']] = data['number']
        except:
            pass

        for milestone in self.tasks_data['milestones']:
            title = milestone['title']
            description = milestone['description']
            due_date = milestone['due_date']

            if title in existing_milestones:
                # Update existing milestone
                milestone_number = existing_milestones[title]
                self._run_gh_command([
                    'api', f'/repos/{self.repo}/milestones/{milestone_number}',
                    '-X', 'PATCH',
                    '-f', f'title={title}',
                    '-f', f'description={description}',
                    '-f', f'due_on={due_date}T23:59:59Z'
                ])
                print(f"  Updated milestone: {title}")
            else:
                # Create new milestone
                self._run_gh_command([
                    'api', f'/repos/{self.repo}/milestones',
                    '-X', 'POST',
                    '-f', f'title={title}',
                    '-f', f'description={description}',
                    '-f', f'due_on={due_date}T23:59:59Z'
                ])
                print(f"  Created milestone: {title}")

    def create_or_update_issues(self):
        """Create or update GitHub issues from tasks"""
        print("\n=== Creating/Updating Issues ===")

        # Get existing issues
        existing_issues = {}
        try:
            output = self._run_gh_command([
                'issue', 'list',
                '--repo', self.repo,
                '--state', 'all',
                '--json', 'number,title,labels,state',
                '--limit', '1000'
            ])
            issues = json.loads(output)
            for issue in issues:
                # Match by title
                existing_issues[issue['title']] = issue
        except:
            pass

        # Get milestones for mapping
        milestone_map = {}
        try:
            output = self._run_gh_command([
                'api', f'/repos/{self.repo}/milestones',
                '--jq', '.[] | {title: .title, number: .number}'
            ])
            for line in output.split('\n'):
                if line.strip():
                    data = json.loads(line)
                    milestone_map[data['title']] = data['number']
        except:
            pass

        # Get milestone titles from tasks data
        milestone_titles = {m['id']: m['title'] for m in self.tasks_data['milestones']}

        for task in self.tasks_data['tasks']:
            title = f"{task['id']}: {task['title']}"
            body = self._create_issue_body(task)
            labels = task.get('labels', [])

            # Add status label
            labels.append(f"status:{task['status']}")

            # Add priority label
            if task.get('priority'):
                labels.append(f"priority:{task['priority']}")

            # Get milestone number
            milestone_number = None
            if task.get('milestone') and task['milestone'] in milestone_titles:
                milestone_title = milestone_titles[task['milestone']]
                milestone_number = milestone_map.get(milestone_title)

            if title in existing_issues:
                # Update existing issue
                issue = existing_issues[title]
                issue_number = issue['number']

                # Determine state
                state = 'closed' if task['status'] == 'completed' else 'open'

                # Update issue
                cmd = [
                    'issue', 'edit', str(issue_number),
                    '--repo', self.repo,
                    '--body', body
                ]

                if labels:
                    cmd.extend(['--add-label', ','.join(labels)])

                if milestone_number:
                    cmd.extend(['--milestone', str(milestone_number)])

                self._run_gh_command(cmd)

                # Update state if needed
                if issue['state'] != state:
                    if state == 'closed':
                        self._run_gh_command(['issue', 'close', str(issue_number), '--repo', self.repo])
                    else:
                        self._run_gh_command(['issue', 'reopen', str(issue_number), '--repo', self.repo])

                print(f"  Updated issue #{issue_number}: {title}")
            else:
                # Create new issue
                cmd = [
                    'issue', 'create',
                    '--repo', self.repo,
                    '--title', title,
                    '--body', body
                ]

                if labels:
                    cmd.extend(['--label', ','.join(labels)])

                if milestone_number:
                    cmd.extend(['--milestone', str(milestone_number)])

                if task.get('assignee'):
                    cmd.extend(['--assignee', task['assignee']])

                output = self._run_gh_command(cmd)
                print(f"  Created issue: {title}")

                # Close issue if already completed
                if task['status'] == 'completed':
                    issue_url = output.strip()
                    issue_number = issue_url.split('/')[-1]
                    self._run_gh_command(['issue', 'close', issue_number, '--repo', self.repo])

    def _create_issue_body(self, task: Dict) -> str:
        """Create issue body from task data"""
        body_parts = [
            task['description'],
            "",
            "### Task Details",
            f"- **Task ID**: {task['id']}",
            f"- **Status**: {task['status']}",
            f"- **Priority**: {task.get('priority', 'N/A')}",
            f"- **Effort**: {task['effort_days']} days",
        ]

        if task.get('milestone'):
            body_parts.append(f"- **Milestone**: {task['milestone']}")

        if task.get('assignee'):
            body_parts.append(f"- **Assignee**: @{task['assignee']}")

        if task.get('dependencies'):
            body_parts.append(f"- **Dependencies**: {', '.join(task['dependencies'])}")

        # Add schedule information if available
        schedule_item = next(
            (s for s in self.schedule_data['schedule'] if s['task_id'] == task['id']),
            None
        )
        if schedule_item:
            body_parts.extend([
                "",
                "### Schedule",
                f"- **Start Date**: {schedule_item['start_date']}",
                f"- **End Date**: {schedule_item['end_date']}",
            ])

        return "\n".join(body_parts)

    def create_project_board(self):
        """Create GitHub Project (Projects V2) and add issues"""
        print("\n=== Creating/Updating Project Board ===")

        project_name = self.tasks_data['project']['name']

        # Check if project exists
        try:
            # List projects
            output = self._run_gh_command([
                'project', 'list',
                '--owner', self.repo.split('/')[0],
                '--format', 'json'
            ])

            projects = json.loads(output)
            existing_project = None

            for project in projects.get('projects', []):
                if project.get('title') == project_name:
                    existing_project = project
                    break

            if existing_project:
                project_number = existing_project.get('number')
                print(f"  Found existing project: {project_name} (#{project_number})")
            else:
                # Create new project
                print(f"  Creating new project: {project_name}")
                print("  Note: Project creation requires organization or user permissions")
                print("  Please create the project manually at:")
                print(f"  https://github.com/{self.repo}/projects")

        except Exception as e:
            print(f"  Note: Project board creation/update requires manual setup")
            print(f"  Please visit: https://github.com/{self.repo}/projects")

    def display_progress(self):
        """Display progress statistics"""
        print("\n=== Progress Summary ===")

        total_tasks = len(self.tasks_data['tasks'])
        completed_tasks = sum(1 for t in self.tasks_data['tasks'] if t['status'] == 'completed')
        in_progress_tasks = sum(1 for t in self.tasks_data['tasks'] if t['status'] == 'in_progress')
        pending_tasks = sum(1 for t in self.tasks_data['tasks'] if t['status'] == 'pending')

        total_effort = sum(t['effort_days'] for t in self.tasks_data['tasks'])
        completed_effort = sum(t['effort_days'] for t in self.tasks_data['tasks'] if t['status'] == 'completed')

        progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        effort_percentage = (completed_effort / total_effort * 100) if total_effort > 0 else 0

        print(f"Repository: {self.repo}")
        print(f"Total Tasks: {total_tasks}")
        print(f"  - Completed: {completed_tasks}")
        print(f"  - In Progress: {in_progress_tasks}")
        print(f"  - Pending: {pending_tasks}")
        print(f"Task Progress: {progress_percentage:.1f}%")
        print(f"Effort Progress: {effort_percentage:.1f}% ({completed_effort}/{total_effort} days)")
        print(f"\nView issues: https://github.com/{self.repo}/issues")
        print(f"View milestones: https://github.com/{self.repo}/milestones")

    def sync(self):
        """Run full synchronization"""
        print(f"Starting GitHub sync for repository: {self.repo}\n")

        if not self.check_gh_cli():
            sys.exit(1)

        self.load_data()
        self.create_or_update_milestones()
        self.create_or_update_issues()
        self.create_project_board()
        self.display_progress()

        print("\n✓ GitHub sync completed successfully!")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Sync tasks.json and schedule.json with GitHub'
    )
    parser.add_argument(
        '--tasks',
        default='tasks.json',
        help='Path to tasks.json file (default: tasks.json)'
    )
    parser.add_argument(
        '--schedule',
        default='schedule.json',
        help='Path to schedule.json file (default: schedule.json)'
    )
    parser.add_argument(
        '--repo',
        help='GitHub repository (owner/repo). Auto-detected if not specified'
    )

    args = parser.parse_args()

    # Validate files exist
    if not os.path.exists(args.tasks):
        print(f"Error: tasks.json not found at {args.tasks}")
        sys.exit(1)

    if not os.path.exists(args.schedule):
        print(f"Error: schedule.json not found at {args.schedule}")
        sys.exit(1)

    try:
        syncer = GitHubSync(args.tasks, args.schedule, args.repo)
        syncer.sync()
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
