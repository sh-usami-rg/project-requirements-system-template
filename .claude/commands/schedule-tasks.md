---
description: Create weekly schedule from tasks.json with date assignment and Gantt chart
---

You are a project scheduling assistant. Your task is to read the tasks.json file and generate a comprehensive schedule with daily, weekly, and monthly views, including a Gantt chart visualization.

## Instructions

1. **Read tasks.json**: Load the task list from the current directory

2. **Generate Daily Schedule**: Create a day-by-day breakdown:
   - List all tasks scheduled for each day
   - Calculate total hours per day
   - Include day of week
   - Show task status and assignee
   - Consider weekends (mark as non-working days if needed)

3. **Generate Weekly Schedule**: Aggregate tasks by week:
   - Group tasks by ISO week number
   - Show week start (Monday) and end (Sunday) dates
   - Calculate total hours per week
   - Calculate weekly progress percentage
   - List all tasks active during that week

4. **Generate Monthly Schedule**: Aggregate tasks by month:
   - Group tasks by month (YYYY-MM format)
   - Show month name
   - Calculate total hours per month
   - Calculate monthly progress percentage
   - List all tasks active during that month

5. **Calculate Progress**: For each level (project, week, month, task):
   - Progress = (completed tasks / total tasks) * 100
   - For individual tasks, calculate based on status:
     - not_started: 0%
     - in_progress: 50% (or use actualHours/estimatedHours if available)
     - completed: 100%
     - blocked: use last known progress
     - cancelled: 0%

6. **Generate Gantt Chart**: Create a visual timeline:
   - List all tasks with their start/end dates
   - Calculate duration in days for each task
   - Show dependencies with arrows/references
   - Include progress bar representation
   - Create ASCII/text-based visualization

7. **Output Format**: Generate a schedule.json file following this structure:

```json
{
  "project": {
    "name": "Project Name",
    "totalTasks": 25,
    "completedTasks": 5,
    "progressPercentage": 20.0,
    "startDate": "YYYY-MM-DD",
    "endDate": "YYYY-MM-DD"
  },
  "dailySchedule": [
    {
      "date": "2026-01-15",
      "dayOfWeek": "Wednesday",
      "tasks": [
        {
          "taskId": "T001",
          "taskName": "Setup development environment",
          "status": "completed",
          "estimatedHours": 8,
          "assignee": "Developer"
        }
      ],
      "totalHours": 8
    }
  ],
  "weeklySchedule": [
    {
      "weekNumber": 3,
      "weekStart": "2026-01-12",
      "weekEnd": "2026-01-18",
      "tasks": [...],
      "totalHours": 40,
      "progressPercentage": 25.0
    }
  ],
  "monthlySchedule": [
    {
      "month": "2026-01",
      "monthName": "January",
      "tasks": [...],
      "totalHours": 160,
      "progressPercentage": 15.0
    }
  ],
  "ganttChart": {
    "timeline": [
      {
        "taskId": "T001",
        "taskName": "Setup development environment",
        "startDate": "2026-01-15",
        "endDate": "2026-01-15",
        "duration": 1,
        "progress": 100,
        "dependencies": []
      }
    ],
    "visualization": "ASCII Gantt chart here"
  },
  "metadata": {
    "generatedAt": "ISO 8601 timestamp",
    "generatedFrom": "tasks.json",
    "version": "1.0"
  }
}
```

## Gantt Chart Visualization Format

Create a text-based Gantt chart like this:

```
Project Timeline (2026-01-15 to 2026-03-31)
============================================================

Task ID  | Task Name                      | Jan      | Feb      | Mar
---------|--------------------------------|----------|----------|----------
T001     | Setup environment              | ████     |          |
T002     | Design database schema         |   ██████ |          |
T003     | Implement API endpoints        |          | ████████ | ██
T004     | Frontend development           |          |     ████ | ████████
T005     | Testing                        |          |          |      ████
---------|--------------------------------|----------|----------|----------

Legend: █ = Task duration, ░ = Completed, █ = In progress, ▒ = Not started
```

## Schedule Generation Rules

1. **Working Hours**: Assume 8 hours per working day
2. **Working Days**: Monday-Friday (exclude weekends)
3. **Task Overlap**: Tasks can run in parallel unless dependencies prevent it
4. **Dependencies**: Ensure dependent tasks don't start before prerequisites complete
5. **Buffer Time**: Add 10% buffer for complex tasks
6. **Milestones**: Identify and highlight major milestones (tasks with multiple dependencies)

## Progress Calculation

```
Project Progress = (Completed Tasks / Total Tasks) * 100

Task Progress:
- not_started: 0%
- in_progress: min(actualHours / estimatedHours * 100, 99%)
- completed: 100%
- blocked: last known progress
- cancelled: treated as 0% for overall calculation

Weekly/Monthly Progress = (Sum of task progress in period / Number of tasks in period)
```

## Important Notes

- Respect task dependencies when scheduling
- Highlight overdue tasks (endDate < today && status != completed)
- Flag resource conflicts (multiple tasks with same assignee on same day)
- Calculate critical path (longest sequence of dependent tasks)
- Show milestones and key deliverables
- Include holidays/non-working days if specified

After generating the schedule, save it as **schedule.json** in the current directory and display:
1. Overall project progress
2. Current week's tasks
3. Upcoming milestones
4. The Gantt chart visualization
5. Any scheduling conflicts or warnings
