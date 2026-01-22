"""
AI Employee Dashboard - Web Interface

FastAPI web application for managing the AI Employee system
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import markdown


app = FastAPI(title="AI Employee Dashboard", description="Web interface for managing AI Employee tasks")

# Mount static files
static_path = Path("static")
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates_path = Path("templates")
templates_path.mkdir(exist_ok=True)
templates = Jinja2Templates(directory="templates")

# Vault paths
VAULT_PATH = Path("./AI_Employee_Vault")
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
IN_PROGRESS_PATH = VAULT_PATH / "In_Progress"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
APPROVED_PATH = VAULT_PATH / "Approved"
DONE_PATH = VAULT_PATH / "Done"


class Task(BaseModel):
    id: str
    title: str
    content: str
    status: str
    priority: str
    category: str
    created_at: str
    source: str
    filepath: str


class ApprovalRequest(BaseModel):
    id: str
    title: str
    content: str
    status: str
    priority: str
    category: str
    created_at: str
    source: str
    filepath: str
    justification: str


def read_task_file(filepath: Path) -> Dict:
    """Read a task markdown file and extract metadata."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract YAML frontmatter if present
    if content.startswith('---'):
        end_frontmatter = content.find('---', 3)
        if end_frontmatter != -1:
            frontmatter = content[4:end_frontmatter].strip()
            import yaml
            metadata = yaml.safe_load(frontmatter) or {}
        else:
            metadata = {}

        # Get the rest of the content after the frontmatter
        main_content = content[end_frontmatter + 3:].strip()
    else:
        metadata = {}
        main_content = content

    # Generate a task ID based on filename
    task_id = filepath.stem.split('_')[0] if '_' in filepath.stem else filepath.stem

    return {
        'id': task_id,
        'title': metadata.get('title', filepath.stem.replace('_', ' ').title()),
        'content': main_content,
        'status': metadata.get('status', 'new'),
        'priority': metadata.get('priority', 'medium'),
        'category': metadata.get('category', 'general'),
        'created_at': metadata.get('created', str(datetime.now().isoformat())),
        'source': metadata.get('source', 'unknown'),
        'filepath': str(filepath)
    }


def get_tasks_by_status(status_folder: str) -> List[Task]:
    """Get all tasks from a specific status folder."""
    folder_map = {
        'needs_action': NEEDS_ACTION_PATH,
        'in_progress': IN_PROGRESS_PATH,
        'pending_approval': PENDING_APPROVAL_PATH,
        'approved': APPROVED_PATH,
        'done': DONE_PATH
    }

    folder_path = folder_map.get(status_folder)
    if not folder_path or not folder_path.exists():
        return []

    tasks = []
    for file_path in folder_path.glob("*.md"):
        try:
            task_data = read_task_file(file_path)
            task = Task(**task_data)
            tasks.append(task)
        except Exception as e:
            print(f"Error reading task file {file_path}: {e}")

    # Sort by creation date (newest first)
    tasks.sort(key=lambda x: x.created_at, reverse=True)
    return tasks


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard showing all task statuses."""
    needs_action_tasks = get_tasks_by_status('needs_action')
    in_progress_tasks = get_tasks_by_status('in_progress')
    pending_approval_tasks = get_tasks_by_status('pending_approval')
    approved_tasks = get_tasks_by_status('approved')
    done_tasks = get_tasks_by_status('done')

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "needs_action_tasks": needs_action_tasks,
        "in_progress_tasks": in_progress_tasks,
        "pending_approval_tasks": pending_approval_tasks,
        "approved_tasks": approved_tasks,
        "done_tasks": done_tasks,
        "total_needs_action": len(needs_action_tasks),
        "total_pending_approval": len(pending_approval_tasks),
        "total_in_progress": len(in_progress_tasks)
    })


@app.get("/tasks/{status}", response_class=HTMLResponse)
async def get_tasks_by_status_page(request: Request, status: str):
    """Page showing tasks for a specific status."""
    tasks = get_tasks_by_status(status)
    return templates.TemplateResponse("tasks_by_status.html", {
        "request": request,
        "tasks": tasks,
        "status": status.title().replace("_", " ")
    })


@app.get("/task/{task_id}", response_class=HTMLResponse)
async def get_task_detail(request: Request, task_id: str):
    """Show detailed view of a specific task."""
    # Search all folders for the task
    all_folders = [NEEDS_ACTION_PATH, IN_PROGRESS_PATH, PENDING_APPROVAL_PATH, APPROVED_PATH, DONE_PATH]

    for folder in all_folders:
        if folder.exists():
            for file_path in folder.glob(f"*{task_id}*.md"):
                task_data = read_task_file(file_path)
                task = Task(**task_data)

                # Convert markdown to HTML
                import markdown
                html_content = markdown.markdown(task.content, extensions=['tables', 'fenced_code'])

                return templates.TemplateResponse("task_detail.html", {
                    "request": request,
                    "task": task,
                    "html_content": html_content
                })

    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/task/{task_id}/move")
async def move_task(task_id: str, destination: str):
    """Move a task from one status to another."""
    # Find the task in any folder
    all_folders = [NEEDS_ACTION_PATH, IN_PROGRESS_PATH, PENDING_APPROVAL_PATH, APPROVED_PATH, DONE_PATH]

    source_file = None
    for folder in all_folders:
        if folder.exists():
            for file_path in folder.glob(f"*{task_id}*.md"):
                source_file = file_path
                break
        if source_file:
            break

    if not source_file:
        raise HTTPException(status_code=404, detail="Task not found")

    # Determine destination folder
    folder_map = {
        'needs_action': NEEDS_ACTION_PATH,
        'in_progress': IN_PROGRESS_PATH,
        'pending_approval': PENDING_APPROVAL_PATH,
        'approved': APPROVED_PATH,
        'done': DONE_PATH
    }

    dest_folder = folder_map.get(destination)
    if not dest_folder:
        raise HTTPException(status_code=400, detail="Invalid destination")

    # Move the file
    dest_path = dest_folder / source_file.name
    source_file.rename(dest_path)

    # Update the status in the file's frontmatter if it has one
    with open(dest_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if content.startswith('---'):
        end_frontmatter = content.find('---', 3)
        if end_frontmatter != -1:
            frontmatter = content[4:end_frontmatter].strip()
            import yaml
            metadata = yaml.safe_load(frontmatter) or {}

            # Update status
            metadata['status'] = destination.replace('_', ' ')

            # Rewrite the file with updated frontmatter
            main_content = content[end_frontmatter + 3:].strip()
            updated_content = f"---\n{yaml.dump(metadata, default_flow_style=False)}\n---\n\n{main_content}"

            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

    return {"message": f"Task moved to {destination}", "task_id": task_id}


@app.get("/api/tasks/{status}")
async def api_get_tasks_by_status(status: str):
    """API endpoint to get tasks by status."""
    tasks = get_tasks_by_status(status)
    return {"tasks": [task.dict() for task in tasks], "status": status}


@app.get("/api/stats")
async def api_get_stats():
    """API endpoint to get dashboard statistics."""
    stats = {
        "needs_action": len(get_tasks_by_status('needs_action')),
        "in_progress": len(get_tasks_by_status('in_progress')),
        "pending_approval": len(get_tasks_by_status('pending_approval')),
        "approved": len(get_tasks_by_status('approved')),
        "done": len(get_tasks_by_status('done')),
    }
    return stats


# Create templates directory and basic templates
template_dashboard = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Employee Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="/static/dashboard.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="fas fa-robot"></i> AI Employee Dashboard
            </a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text">
                    <i class="fas fa-chart-bar"></i>
                    Needs Action: <span class="badge bg-warning text-dark">{{ total_needs_action }}</span>
                    Pending Approval: <span class="badge bg-info text-white">{{ total_pending_approval }}</span>
                </span>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <div class="row">
            <!-- Needs Action Column -->
            <div class="col-md-4 mb-4">
                <div class="card border-warning">
                    <div class="card-header bg-warning text-dark d-flex justify-content-between align-items-center">
                        <h5 class="mb-0"><i class="fas fa-exclamation-circle"></i> Needs Action</h5>
                        <span class="badge bg-secondary">{{ total_needs_action }}</span>
                    </div>
                    <div class="card-body p-0">
                        {% if needs_action_tasks %}
                            <div class="list-group list-group-flush">
                                {% for task in needs_action_tasks %}
                                    <a href="/task/{{ task.id }}" class="list-group-item list-group-item-action">
                                        <div class="d-flex w-100 justify-content-between">
                                            <h6 class="mb-1">{{ task.title }}</h6>
                                            <small>{{ task.priority.title() }}</small>
                                        </div>
                                        <p class="mb-1">{{ task.content[:100] }}{% if task.content|length > 100 %}...{% endif %}</p>
                                        <small class="text-muted">{{ task.source }} | {{ task.created_at[:19] }}</small>
                                    </a>
                                {% endfor %}
                            </div>
                        {% else %}
                            <div class="card-body text-center text-muted">
                                <i class="fas fa-inbox fa-2x mb-2"></i>
                                <p>No tasks need action</p>
                            </div>
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- In Progress Column -->
            <div class="col-md-4 mb-4">
                <div class="card border-info">
                    <div class="card-header bg-info text-white d-flex justify-content-between align-items-center">
                        <h5 class="mb-0"><i class="fas fa-cogs"></i> In Progress</h5>
                        <span class="badge bg-secondary">{{ total_in_progress }}</span>
                    </div>
                    <div class="card-body p-0">
                        {% if in_progress_tasks %}
                            <div class="list-group list-group-flush">
                                {% for task in in_progress_tasks %}
                                    <a href="/task/{{ task.id }}" class="list-group-item list-group-item-action">
                                        <div class="d-flex w-100 justify-content-between">
                                            <h6 class="mb-1">{{ task.title }}</h6>
                                            <small>{{ task.priority.title() }}</small>
                                        </div>
                                        <p class="mb-1">{{ task.content[:100] }}{% if task.content|length > 100 %}...{% endif %}</p>
                                        <small class="text-muted">{{ task.source }} | {{ task.created_at[:19] }}</small>
                                    </a>
                                {% endfor %}
                            </div>
                        {% else %}
                            <div class="card-body text-center text-muted">
                                <i class="fas fa-spinner fa-2x mb-2"></i>
                                <p>No tasks in progress</p>
                            </div>
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- Pending Approval Column -->
            <div class="col-md-4 mb-4">
                <div class="card border-danger">
                    <div class="card-header bg-danger text-white d-flex justify-content-between align-items-center">
                        <h5 class="mb-0"><i class="fas fa-user-clock"></i> Pending Approval</h5>
                        <span class="badge bg-secondary">{{ total_pending_approval }}</span>
                    </div>
                    <div class="card-body p-0">
                        {% if pending_approval_tasks %}
                            <div class="list-group list-group-flush">
                                {% for task in pending_approval_tasks %}
                                    <div class="list-group-item">
                                        <div class="d-flex w-100 justify-content-between">
                                            <h6 class="mb-1">{{ task.title }}</h6>
                                            <small>{{ task.priority.title() }}</small>
                                        </div>
                                        <p class="mb-1">{{ task.content[:100] }}{% if task.content|length > 100 %}...{% endif %}</p>
                                        <small class="text-muted">{{ task.source }} | {{ task.created_at[:19] }}</small>
                                        <div class="mt-2">
                                            <button class="btn btn-sm btn-success me-2" onclick="moveTask('{{ task.id }}', 'approved')">
                                                <i class="fas fa-check"></i> Approve
                                            </button>
                                            <button class="btn btn-sm btn-secondary" onclick="moveTask('{{ task.id }}', 'rejected')">
                                                <i class="fas fa-times"></i> Reject
                                            </button>
                                        </div>
                                    </div>
                                {% endfor %}
                            </div>
                        {% else %}
                            <div class="card-body text-center text-muted">
                                <i class="fas fa-check-circle fa-2x mb-2"></i>
                                <p>No tasks pending approval</p>
                            </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <!-- Approved Column -->
            <div class="col-md-6 mb-4">
                <div class="card border-success">
                    <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
                        <h5 class="mb-0"><i class="fas fa-check-circle"></i> Approved</h5>
                        <span class="badge bg-light text-dark">{{ approved_tasks|length }}</span>
                    </div>
                    <div class="card-body p-0">
                        {% if approved_tasks %}
                            <div class="list-group list-group-flush">
                                {% for task in approved_tasks %}
                                    <a href="/task/{{ task.id }}" class="list-group-item list-group-item-action">
                                        <div class="d-flex w-100 justify-content-between">
                                            <h6 class="mb-1">{{ task.title }}</h6>
                                            <small>{{ task.priority.title() }}</small>
                                        </div>
                                        <p class="mb-1">{{ task.content[:100] }}{% if task.content|length > 100 %}...{% endif %}</p>
                                        <small class="text-muted">{{ task.source }} | {{ task.created_at[:19] }}</small>
                                    </a>
                                {% endfor %}
                            </div>
                        {% else %}
                            <div class="card-body text-center text-muted">
                                <i class="fas fa-thumbs-up fa-2x mb-2"></i>
                                <p>No approved tasks</p>
                            </div>
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- Done Column -->
            <div class="col-md-6 mb-4">
                <div class="card border-secondary">
                    <div class="card-header bg-secondary text-white d-flex justify-content-between align-items-center">
                        <h5 class="mb-0"><i class="fas fa-check-double"></i> Done</h5>
                        <span class="badge bg-light text-dark">{{ done_tasks|length }}</span>
                    </div>
                    <div class="card-body p-0">
                        {% if done_tasks %}
                            <div class="list-group list-group-flush">
                                {% for task in done_tasks %}
                                    <a href="/task/{{ task.id }}" class="list-group-item list-group-item-action">
                                        <div class="d-flex w-100 justify-content-between">
                                            <h6 class="mb-1">{{ task.title }}</h6>
                                            <small>{{ task.priority.title() }}</small>
                                        </div>
                                        <p class="mb-1">{{ task.content[:100] }}{% if task.content|length > 100 %}...{% endif %}</p>
                                        <small class="text-muted">{{ task.source }} | {{ task.created_at[:19] }}</small>
                                    </a>
                                {% endfor %}
                            </div>
                        {% else %}
                            <div class="card-body text-center text-muted">
                                <i class="fas fa-clipboard-list fa-2x mb-2"></i>
                                <p>No completed tasks</p>
                            </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/dashboard.js"></script>
</body>
</html>'''

template_task_detail = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ task.title }} - AI Employee Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h4 class="mb-0">{{ task.title }}</h4>
                <span class="badge bg-{{ 'danger' if task.priority == 'high' else 'warning' if task.priority == 'medium' else 'secondary' }}">
                    {{ task.priority.title() }}
                </span>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Status:</strong>
                        <span class="badge bg-{{ 'primary' if task.status == 'new' else 'info' if task.status == 'in_progress' else 'warning' if task.status == 'pending_approval' else 'success' }}">
                            {{ task.status.replace('_', ' ').title() }}
                        </span>
                    </div>
                    <div class="col-md-6">
                        <strong>Category:</strong> {{ task.category.title() }}
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Source:</strong> {{ task.source }}
                    </div>
                    <div class="col-md-6">
                        <strong>Created:</strong> {{ task.created_at[:19] }}
                    </div>
                </div>

                <hr>

                <div class="task-content">
                    {{ html_content|safe }}
                </div>
            </div>
            <div class="card-footer">
                <div class="btn-toolbar gap-2" role="toolbar">
                    {% if task.status != 'approved' %}
                        <button class="btn btn-success" onclick="moveTask('{{ task.id }}', 'approved')">
                            <i class="fas fa-check"></i> Approve
                        </button>
                    {% endif %}

                    {% if task.status != 'in_progress' %}
                        <button class="btn btn-info" onclick="moveTask('{{ task.id }}', 'in_progress')">
                            <i class="fas fa-play"></i> Start Progress
                        </button>
                    {% endif %}

                    {% if task.status != 'done' %}
                        <button class="btn btn-primary" onclick="moveTask('{{ task.id }}', 'done')">
                            <i class="fas fa-check-circle"></i> Mark Done
                        </button>
                    {% endif %}

                    <button class="btn btn-secondary" onclick="history.back()">
                        <i class="fas fa-arrow-left"></i> Back
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        async function moveTask(taskId, destination) {
            try {
                const response = await fetch(`/task/${taskId}/move?destination=${destination}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                if (response.ok) {
                    // Redirect back to dashboard after successful move
                    window.location.href = '/';
                } else {
                    alert('Error moving task');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error moving task');
            }
        }
    </script>
</body>
</html>'''

# Write templates
with open("templates/dashboard.html", "w", encoding="utf-8") as f:
    f.write(template_dashboard)

with open("templates/task_detail.html", "w", encoding="utf-8") as f:
    f.write(template_task_detail)

# Create static directory and CSS
css_content = '''
:root {
    --needs-action-color: #ffc107;
    --in-progress-color: #17a2b8;
    --pending-approval-color: #dc3545;
    --approved-color: #28a745;
    --done-color: #6c757d;
}

body {
    background-color: #f8f9fa;
}

.card {
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    border: 1px solid rgba(0, 0, 0, 0.125);
    margin-bottom: 1rem;
}

.card-header {
    font-weight: 600;
}

.list-group-item {
    border-left: 0;
    border-right: 0;
    border-radius: 0;
}

.list-group-item:first-child {
    border-top: 0;
}

.list-group-item:last-child {
    border-bottom: 0;
}

.navbar-brand {
    font-weight: bold;
}

.badge {
    font-size: 0.8em;
}

.task-content {
    line-height: 1.6;
}

.task-content h1, .task-content h2, .task-content h3 {
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}

.task-content h1 {
    font-size: 1.75rem;
    border-bottom: 2px solid #eee;
    padding-bottom: 0.3rem;
}

.task-content h2 {
    font-size: 1.5rem;
    border-bottom: 1px solid #eee;
    padding-bottom: 0.3rem;
}

.task-content h3 {
    font-size: 1.25rem;
}

.task-content p {
    margin-bottom: 1rem;
}

.task-content ul, .task-content ol {
    margin-bottom: 1rem;
    padding-left: 1.5rem;
}

.task-content li {
    margin-bottom: 0.25rem;
}

.task-content table {
    width: 100%;
    margin-bottom: 1rem;
    border-collapse: collapse;
}

.task-content table th,
.task-content table td {
    padding: 0.5rem;
    border: 1px solid #dee2e6;
}

.task-content table th {
    background-color: #f8f9fa;
    font-weight: 600;
}

.task-content pre {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 0.375rem;
    padding: 1rem;
    overflow-x: auto;
    margin-bottom: 1rem;
}

.task-content code {
    background-color: #f8f9fa;
    padding: 0.2rem 0.4rem;
    border-radius: 0.25rem;
    font-size: 0.875em;
}
'''

js_content = '''
async function moveTask(taskId, destination) {
    try {
        const response = await fetch(`/task/${taskId}/move?destination=${destination}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            // Reload the page to reflect changes
            location.reload();
        } else {
            const result = await response.json();
            alert(`Error: ${result.detail || 'Failed to move task'}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error connecting to server');
    }
}

// Add drag and drop functionality for task cards
document.addEventListener('DOMContentLoaded', function() {
    const draggableElements = document.querySelectorAll('.list-group-item');

    draggableElements.forEach(element => {
        element.draggable = true;

        element.addEventListener('dragstart', function(e) {
            e.dataTransfer.setData('text/plain', element.querySelector('a').href.split('/').pop());
        });
    });

    const dropZones = document.querySelectorAll('.card-body.p-0');

    dropZones.forEach(zone => {
        zone.addEventListener('dragover', function(e) {
            e.preventDefault();
            zone.style.backgroundColor = '#f8f9fa';
        });

        zone.addEventListener('dragleave', function(e) {
            zone.style.backgroundColor = '';
        });

        zone.addEventListener('drop', function(e) {
            e.preventDefault();
            zone.style.backgroundColor = '';

            const taskId = e.dataTransfer.getData('text/plain');
            const destination = zone.closest('.card').querySelector('.card-header').textContent.trim().split(' ')[0].toLowerCase();

            if (taskId && destination) {
                moveTask(taskId, destination);
            }
        });
    });
});
'''

with open("static/dashboard.css", "w", encoding="utf-8") as f:
    f.write(css_content)

with open("static/dashboard.js", "w", encoding="utf-8") as f:
    f.write(js_content)