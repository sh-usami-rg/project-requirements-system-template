#!/bin/bash
#
# GitHub Sync Script (Bash version)
# Synchronizes tasks.json with GitHub Issues, Projects, and Milestones
#
# Usage: ./github-sync.sh [--repo OWNER/REPO] [--tasks PATH] [--schedule PATH]
#

set -e

# Default values
TASKS_FILE="tasks.json"
SCHEDULE_FILE="schedule.json"
REPO=""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --repo)
            REPO="$2"
            shift 2
            ;;
        --tasks)
            TASKS_FILE="$2"
            shift 2
            ;;
        --schedule)
            SCHEDULE_FILE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --repo OWNER/REPO    GitHub repository (auto-detected if not specified)"
            echo "  --tasks PATH         Path to tasks.json (default: tasks.json)"
            echo "  --schedule PATH      Path to schedule.json (default: schedule.json)"
            echo "  -h, --help          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}→${NC} $1"
}

# Check if gh CLI is installed
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is not installed"
        echo "Please install gh CLI: https://cli.github.com/"
        exit 1
    fi

    # Check authentication
    if ! gh auth status &> /dev/null; then
        print_error "GitHub CLI is not authenticated"
        echo "Please run: gh auth login"
        exit 1
    fi

    print_success "GitHub CLI is authenticated"
}

# Check if jq is installed
check_jq() {
    if ! command -v jq &> /dev/null; then
        print_error "jq is not installed"
        echo "Please install jq:"
        echo "  macOS: brew install jq"
        echo "  Linux: sudo apt install jq (Debian/Ubuntu) or sudo yum install jq (RHEL/CentOS)"
        exit 1
    fi
}

# Auto-detect repository from git remote
detect_repo() {
    if [ -z "$REPO" ]; then
        if ! git remote get-url origin &> /dev/null; then
            print_error "Not in a git repository or no remote configured"
            echo "Please specify repository with --repo OWNER/REPO"
            exit 1
        fi

        REMOTE_URL=$(git remote get-url origin)

        # Parse GitHub URL
        if [[ $REMOTE_URL == git@github.com:* ]]; then
            REPO=$(echo "$REMOTE_URL" | sed 's/git@github.com://g' | sed 's/.git$//g')
        elif [[ $REMOTE_URL == *github.com/* ]]; then
            REPO=$(echo "$REMOTE_URL" | sed 's/.*github.com\///g' | sed 's/.git$//g')
        else
            print_error "Not a GitHub repository"
            exit 1
        fi
    fi

    print_success "Repository: $REPO"
}

# Check if files exist
check_files() {
    if [ ! -f "$TASKS_FILE" ]; then
        print_error "tasks.json not found at $TASKS_FILE"
        exit 1
    fi

    if [ ! -f "$SCHEDULE_FILE" ]; then
        print_error "schedule.json not found at $SCHEDULE_FILE"
        exit 1
    fi

    TASK_COUNT=$(jq '.tasks | length' "$TASKS_FILE")
    print_success "Loaded $TASK_COUNT tasks from $TASKS_FILE"

    SCHEDULE_COUNT=$(jq '.schedule | length' "$SCHEDULE_FILE")
    print_success "Loaded $SCHEDULE_COUNT scheduled items from $SCHEDULE_FILE"
}

# Create or update milestones
sync_milestones() {
    echo ""
    echo "=== Creating/Updating Milestones ==="

    # Get existing milestones
    EXISTING_MILESTONES=$(gh api "/repos/$REPO/milestones" --jq '.[] | {title: .title, number: .number}' 2>/dev/null || echo "[]")

    # Read milestones from tasks.json
    MILESTONE_COUNT=$(jq '.milestones | length' "$TASKS_FILE")

    for i in $(seq 0 $((MILESTONE_COUNT - 1))); do
        TITLE=$(jq -r ".milestones[$i].title" "$TASKS_FILE")
        DESCRIPTION=$(jq -r ".milestones[$i].description" "$TASKS_FILE")
        DUE_DATE=$(jq -r ".milestones[$i].due_date" "$TASKS_FILE")

        # Check if milestone exists
        MILESTONE_NUMBER=$(echo "$EXISTING_MILESTONES" | jq -r "select(.title == \"$TITLE\") | .number" | head -n 1)

        if [ -n "$MILESTONE_NUMBER" ] && [ "$MILESTONE_NUMBER" != "null" ]; then
            # Update existing milestone
            gh api "/repos/$REPO/milestones/$MILESTONE_NUMBER" \
                -X PATCH \
                -f title="$TITLE" \
                -f description="$DESCRIPTION" \
                -f due_on="${DUE_DATE}T23:59:59Z" &> /dev/null

            print_info "Updated milestone: $TITLE"
        else
            # Create new milestone
            gh api "/repos/$REPO/milestones" \
                -X POST \
                -f title="$TITLE" \
                -f description="$DESCRIPTION" \
                -f due_on="${DUE_DATE}T23:59:59Z" &> /dev/null

            print_info "Created milestone: $TITLE"
        fi
    done
}

# Create or update issues
sync_issues() {
    echo ""
    echo "=== Creating/Updating Issues ==="

    # Get existing issues
    EXISTING_ISSUES=$(gh issue list --repo "$REPO" --state all --json number,title,state --limit 1000)

    # Get milestone mapping
    MILESTONE_MAP=$(gh api "/repos/$REPO/milestones" --jq '.[] | {title: .title, number: .number}')

    # Read milestone titles
    MILESTONE_TITLES=$(jq -r '.milestones[] | "\(.id)|\(.title)"' "$TASKS_FILE")

    # Read tasks from tasks.json
    TASK_COUNT=$(jq '.tasks | length' "$TASKS_FILE")

    for i in $(seq 0 $((TASK_COUNT - 1))); do
        TASK_ID=$(jq -r ".tasks[$i].id" "$TASKS_FILE")
        TASK_TITLE=$(jq -r ".tasks[$i].title" "$TASKS_FILE")
        FULL_TITLE="${TASK_ID}: ${TASK_TITLE}"
        DESCRIPTION=$(jq -r ".tasks[$i].description" "$TASKS_FILE")
        STATUS=$(jq -r ".tasks[$i].status" "$TASKS_FILE")
        PRIORITY=$(jq -r ".tasks[$i].priority" "$TASKS_FILE")
        EFFORT=$(jq -r ".tasks[$i].effort_days" "$TASKS_FILE")
        MILESTONE_ID=$(jq -r ".tasks[$i].milestone" "$TASKS_FILE")
        ASSIGNEE=$(jq -r ".tasks[$i].assignee" "$TASKS_FILE")
        LABELS=$(jq -r ".tasks[$i].labels | join(\",\")" "$TASKS_FILE")

        # Add status and priority labels
        ALL_LABELS="status:${STATUS},priority:${PRIORITY}"
        if [ -n "$LABELS" ] && [ "$LABELS" != "null" ]; then
            ALL_LABELS="${ALL_LABELS},${LABELS}"
        fi

        # Get milestone number
        MILESTONE_TITLE=$(echo "$MILESTONE_TITLES" | grep "^${MILESTONE_ID}|" | cut -d'|' -f2)
        MILESTONE_NUMBER=""
        if [ -n "$MILESTONE_TITLE" ] && [ "$MILESTONE_TITLE" != "null" ]; then
            MILESTONE_NUMBER=$(echo "$MILESTONE_MAP" | jq -r "select(.title == \"$MILESTONE_TITLE\") | .number" | head -n 1)
        fi

        # Get schedule info
        SCHEDULE_INFO=$(jq -r ".schedule[] | select(.task_id == \"$TASK_ID\") | \"Start: \(.start_date), End: \(.end_date)\"" "$SCHEDULE_FILE")

        # Create issue body
        BODY="$DESCRIPTION

### Task Details
- **Task ID**: $TASK_ID
- **Status**: $STATUS
- **Priority**: $PRIORITY
- **Effort**: $EFFORT days"

        if [ -n "$MILESTONE_ID" ] && [ "$MILESTONE_ID" != "null" ]; then
            BODY="$BODY
- **Milestone**: $MILESTONE_ID"
        fi

        if [ -n "$SCHEDULE_INFO" ]; then
            BODY="$BODY

### Schedule
- $SCHEDULE_INFO"
        fi

        # Check if issue exists
        ISSUE_NUMBER=$(echo "$EXISTING_ISSUES" | jq -r ".[] | select(.title == \"$FULL_TITLE\") | .number" | head -n 1)

        if [ -n "$ISSUE_NUMBER" ] && [ "$ISSUE_NUMBER" != "null" ]; then
            # Update existing issue
            gh issue edit "$ISSUE_NUMBER" \
                --repo "$REPO" \
                --body "$BODY" \
                --add-label "$ALL_LABELS" &> /dev/null

            if [ -n "$MILESTONE_NUMBER" ] && [ "$MILESTONE_NUMBER" != "null" ]; then
                gh api "/repos/$REPO/issues/$ISSUE_NUMBER" \
                    -X PATCH \
                    -f milestone="$MILESTONE_NUMBER" &> /dev/null
            fi

            # Update state
            CURRENT_STATE=$(echo "$EXISTING_ISSUES" | jq -r ".[] | select(.number == $ISSUE_NUMBER) | .state")
            if [ "$STATUS" == "completed" ] && [ "$CURRENT_STATE" == "OPEN" ]; then
                gh issue close "$ISSUE_NUMBER" --repo "$REPO" &> /dev/null
            elif [ "$STATUS" != "completed" ] && [ "$CURRENT_STATE" == "CLOSED" ]; then
                gh issue reopen "$ISSUE_NUMBER" --repo "$REPO" &> /dev/null
            fi

            print_info "Updated issue #$ISSUE_NUMBER: $FULL_TITLE"
        else
            # Create new issue
            CREATE_CMD="gh issue create --repo $REPO --title \"$FULL_TITLE\" --body \"$BODY\" --label \"$ALL_LABELS\""

            if [ -n "$MILESTONE_NUMBER" ] && [ "$MILESTONE_NUMBER" != "null" ]; then
                CREATE_CMD="$CREATE_CMD --milestone \"$MILESTONE_NUMBER\""
            fi

            if [ -n "$ASSIGNEE" ] && [ "$ASSIGNEE" != "null" ] && [ "$ASSIGNEE" != "" ]; then
                CREATE_CMD="$CREATE_CMD --assignee \"$ASSIGNEE\""
            fi

            ISSUE_URL=$(eval "$CREATE_CMD")
            NEW_ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -o '[0-9]*$')

            print_info "Created issue #$NEW_ISSUE_NUMBER: $FULL_TITLE"

            # Close if already completed
            if [ "$STATUS" == "completed" ]; then
                gh issue close "$NEW_ISSUE_NUMBER" --repo "$REPO" &> /dev/null
            fi
        fi
    done
}

# Display progress summary
display_progress() {
    echo ""
    echo "=== Progress Summary ==="

    TOTAL_TASKS=$(jq '.tasks | length' "$TASKS_FILE")
    COMPLETED_TASKS=$(jq '[.tasks[] | select(.status == "completed")] | length' "$TASKS_FILE")
    IN_PROGRESS_TASKS=$(jq '[.tasks[] | select(.status == "in_progress")] | length' "$TASKS_FILE")
    PENDING_TASKS=$(jq '[.tasks[] | select(.status == "pending")] | length' "$TASKS_FILE")

    TOTAL_EFFORT=$(jq '[.tasks[].effort_days] | add' "$TASKS_FILE")
    COMPLETED_EFFORT=$(jq '[.tasks[] | select(.status == "completed") | .effort_days] | add // 0' "$TASKS_FILE")

    TASK_PROGRESS=$(echo "scale=1; $COMPLETED_TASKS * 100 / $TOTAL_TASKS" | bc)
    EFFORT_PROGRESS=$(echo "scale=1; $COMPLETED_EFFORT * 100 / $TOTAL_EFFORT" | bc)

    echo "Repository: $REPO"
    echo "Total Tasks: $TOTAL_TASKS"
    echo "  - Completed: $COMPLETED_TASKS"
    echo "  - In Progress: $IN_PROGRESS_TASKS"
    echo "  - Pending: $PENDING_TASKS"
    echo "Task Progress: ${TASK_PROGRESS}%"
    echo "Effort Progress: ${EFFORT_PROGRESS}% (${COMPLETED_EFFORT}/${TOTAL_EFFORT} days)"
    echo ""
    echo "View issues: https://github.com/$REPO/issues"
    echo "View milestones: https://github.com/$REPO/milestones"
}

# Main execution
main() {
    echo "Starting GitHub sync..."
    echo ""

    check_gh_cli
    check_jq
    detect_repo
    check_files
    sync_milestones
    sync_issues
    display_progress

    echo ""
    print_success "GitHub sync completed successfully!"
}

# Run main function
main
