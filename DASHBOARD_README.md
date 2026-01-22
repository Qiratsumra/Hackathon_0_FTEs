# 🎨 AI Employee Dashboard

A web-based dashboard for managing your AI Employee system tasks, approvals, and operations.

## 🚀 Quick Start

### Start the Dashboard Server

```bash
python run_dashboard.py
```

### Access the Dashboard

Open your browser and go to: [http://localhost:8000](http://localhost:8000)

## 📋 Features

### Task Management
- **Visual Kanban Board**: See tasks organized by status (Needs Action, In Progress, Pending Approval, etc.)
- **Task Details**: Click on any task to see full details and content
- **Drag & Drop**: Move tasks between statuses (coming soon)

### Approval System
- **Pending Approvals**: See all tasks requiring your approval
- **One-Click Approval**: Approve or reject tasks with a single click
- **Status Tracking**: Track approval status in real-time

### Task Navigation
- **Status Columns**: Tasks organized by status for easy scanning
- **Priority Indicators**: Visual indicators for task priority (High/Medium/Low)
- **Quick Actions**: Move tasks between statuses directly from the dashboard

## 🏗️ Architecture

### Backend (FastAPI)
- RESTful API endpoints
- Task management operations
- File system integration with AI Employee vault
- Real-time statistics

### Frontend (HTML/CSS/JS)
- Responsive Bootstrap interface
- Interactive task management
- Real-time updates
- Mobile-friendly design

### Templates
- `dashboard.html`: Main dashboard view with all task columns
- `task_detail.html`: Detailed view of individual tasks
- `tasks_by_status.html`: Filtered views by status (future)

## 🛠️ API Endpoints

- `GET /` - Main dashboard view
- `GET /task/{task_id}` - Detailed task view
- `POST /task/{task_id}/move` - Move task between statuses
- `GET /api/tasks/{status}` - Get tasks by status (JSON)
- `GET /api/stats` - Get dashboard statistics (JSON)

## 🔧 Development

### Adding New Features

1. **Backend**: Add new endpoints in `dashboard_api.py`
2. **Frontend**: Update templates in `templates/` directory
3. **Styling**: Update CSS in `static/dashboard.css`
4. **JavaScript**: Add interactivity in `static/dashboard.js`

### Customizing the Dashboard

- Modify `templates/dashboard.html` to change layout
- Update `static/dashboard.css` for styling changes
- Add new JavaScript functionality in `static/dashboard.js`

## 🚨 Troubleshooting

### Server Won't Start
- Ensure all dependencies are installed: `pip install fastapi uvicorn jinja2 python-multipart markdown pyyaml`
- Check that port 8000 is available

### Dashboard Not Loading
- Verify the server is running
- Check browser console for errors
- Ensure templates and static files exist

### Task Not Appearing
- Verify the task exists in the appropriate vault folder
- Check file permissions on the vault directory

## 📊 Usage Tips

1. **Keep the server running** for continuous dashboard access
2. **Refresh the page** to see new tasks or status changes
3. **Use the back button** in the task detail view to return to dashboard
4. **Check the navigation bar** for quick access to important stats

## 🔄 Integration

The dashboard integrates seamlessly with your existing AI Employee system:
- Reads tasks from `AI_Employee_Vault/` folders
- Updates task statuses by moving files between folders
- Maintains all existing security and approval workflows
- Preserves existing logging and audit trails

## 🎯 Next Enhancements

Future features planned:
- Real-time notifications
- Advanced filtering and search
- Email composition interface
- Task assignment and delegation
- Performance analytics
- Export functionality