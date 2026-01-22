# Orchestrator Component

The Orchestrator is the master coordinator that manages all components of the AI Employee system.

## Overview

The Orchestrator serves as the central hub of the AI Employee System, coordinating between various components and managing the workflow of tasks through the system.

## Responsibilities

- Monitors vault folders for changes
- Triggers Claude Code when new tasks appear
- Processes approved actions
- Handles scheduled tasks
- Maintains health checks and process management
- Coordinates between different system components

## Key Methods

### `trigger_claude_processing(task_info)`
Processes a task file with Claude Code to determine next actions and generate plans.

### `move_task_file(source_file, destination_folder)`
Moves task files between different vault folders as they progress through their lifecycle.

### `run_health_checks()`
Performs periodic health checks on all system components.

### `generate_daily_briefing()`
Creates daily status briefings summarizing system activity.

## Vault Folder Management

The orchestrator manages several key folders:

- `Needs_Action`: New tasks requiring processing
- `Plans`: Generated work plans
- `In_Progress`: Currently active tasks
- `Pending_Approval`: Tasks awaiting human approval
- `Approved`: Approved tasks ready for execution
- `Done`: Completed tasks
- `Logs`: Activity logs
- `Briefings`: CEO briefings

## Event Handling

The orchestrator responds to file system events:

- **File Creation**: New task files trigger Claude processing
- **File Modification**: Changes to existing files are monitored
- **Scheduled Events**: Periodic tasks like health checks and briefings

## Error Handling

The orchestrator implements comprehensive error handling:

- Task processing errors are logged and escalated
- Failed tasks are moved to appropriate error folders
- System component failures are detected and reported
- Graceful degradation when components are unavailable