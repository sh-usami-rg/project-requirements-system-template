---
description: Create project plan from SPEC.md with WBS, effort estimation, and task breakdown
---

You are a project planning assistant. Your task is to read the SPEC.md file in the current directory and generate a comprehensive project plan with tasks breakdown.

## Instructions

1. **Read SPEC.md**: Analyze the specification document to understand:
   - Project goals and objectives
   - Features and functionalities
   - Technical requirements
   - Deliverables
   - Any mentioned constraints or dependencies

2. **Generate Work Breakdown Structure (WBS)**: Create a hierarchical task list that includes:
   - Main phases (planning, design, development, testing, deployment, etc.)
   - Major features as top-level tasks
   - Sub-tasks breaking down each feature into actionable items
   - Each task should have a unique ID (T001, T002, etc.)

3. **Estimate Effort**: For each task, provide:
   - Estimated hours (be realistic based on complexity)
   - Consider dependencies and sequential vs. parallel work
   - Account for testing, documentation, and review time

4. **Set Dates**: Assign start and end dates to each task:
   - Start from today's date or a specified project start date
   - Account for dependencies (tasks that must complete before others start)
   - Assume an 8-hour workday for calculations
   - Allow buffer time for complex tasks

5. **Categorize and Prioritize**: For each task:
   - Category: planning, design, development, testing, documentation, deployment, other
   - Priority: critical, high, medium, low
   - Status: not_started (default for new plans)
   - Tags: add relevant tags for filtering/searching

6. **Output Format**: Generate a tasks.json file following this structure:

```json
{
  "project": {
    "name": "Project Name from SPEC",
    "description": "Brief project description",
    "startDate": "YYYY-MM-DD",
    "endDate": "YYYY-MM-DD"
  },
  "tasks": [
    {
      "id": "T001",
      "name": "Task name",
      "description": "Detailed description",
      "category": "development",
      "priority": "high",
      "status": "not_started",
      "startDate": "YYYY-MM-DD",
      "endDate": "YYYY-MM-DD",
      "estimatedHours": 16,
      "actualHours": 0,
      "assignee": "",
      "dependencies": [],
      "subtasks": ["T002", "T003"],
      "tags": ["backend", "api"],
      "notes": "Additional notes"
    }
  ],
  "metadata": {
    "generatedAt": "ISO 8601 timestamp",
    "generatedFrom": "SPEC.md",
    "version": "1.0"
  }
}
```

## Task Breakdown Guidelines

- **Planning Phase**: Requirements analysis, architecture design, tech stack selection
- **Design Phase**: UI/UX design, database schema, API design, system architecture
- **Development Phase**: Break down by feature/module, include setup tasks
- **Testing Phase**: Unit tests, integration tests, E2E tests, UAT
- **Documentation Phase**: Code comments, API docs, user guides, README
- **Deployment Phase**: Environment setup, CI/CD, deployment, monitoring

## Estimation Guidelines

- Simple CRUD operations: 2-4 hours
- API endpoint development: 4-8 hours
- Complex feature: 16-40 hours
- UI component: 4-8 hours
- Integration work: 8-16 hours
- Testing (per feature): 25-30% of development time
- Documentation: 10-15% of development time

## Important Notes

- Be thorough but realistic with estimates
- Include time for code review and iterations
- Consider learning curve for new technologies
- Add buffer for unexpected issues
- Dependencies should reference task IDs
- Subtasks should be listed in the parent task's subtasks array

After generating the plan, save it as **tasks.json** in the current directory and provide a summary showing:
- Total number of tasks
- Total estimated hours
- Project duration (start to end date)
- Tasks by category
- Critical path tasks
