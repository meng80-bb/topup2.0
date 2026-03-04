---
name: topup-api
description: "Interact with Topup HTTP API for task and workflow management. Use when: (1) Creating or managing data processing tasks, (2) Checking task status/progress, (3) Querying workflow definitions, (4) Downloading task results/logs, (5) Managing task execution (start/pause/resume/cancel). Base URL: http://0.0.0.0:5000"
---

# Topup HTTP API

## Quick Start

Base URL: `http://0.0.0.0:5000`

```bash
# Health check
curl http://0.0.0.0:5000/api/health

# Create a task
curl -X POST http://0.0.0.0:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "workflow_name": "topup_standard_workflow",
    "task_name": "处理250624日期数据",
    "parameters": {
      "date_param": "250624",
      "submit_job": true,
      "max_wait_minutes": 25
    }
  }'
```

## Task Management

### Create Task

```bash
POST /api/tasks
Content-Type: application/json

{
    "user_id": "user123",
    "workflow_name": "topup_standard_workflow",
    "task_name": "处理250624日期数据",
    "parameters": {
        "date_param": "250624",
        "submit_job": true,
        "max_wait_minutes": 25
    }
}
```

Available workflows:
- `topup_standard_workflow` - Full Topup data processing (5 steps)
- `get_available_dates` - Get available dates

### List Tasks

```bash
GET /api/tasks?user_id=user123&status=running&limit=10&offset=0
```

Parameters:
- `user_id` (required): User ID
- `status` (optional): pending/running/completed/failed/cancelled
- `limit` (optional): Default 10
- `offset` (optional): Default 0

### Get Task Details

```bash
GET /api/tasks/{task_id}
```

### Task Operations

```bash
# Start task
POST /api/tasks/{task_id}/start

# Pause task
POST /api/tasks/{task_id}/pause

# Resume task
POST /api/tasks/{task_id}/resume

# Cancel task
POST /api/tasks/{task_id}/cancel
```

### Task Progress & Logs

```bash
# Get progress
GET /api/tasks/{task_id}/progress

# Get logs
GET /api/tasks/{task_id}/logs?level=error&limit=100
```

Log levels: info/warning/error/debug

## Workflow Management

### List Workflows

```bash
GET /api/workflows
```

### Get Workflow Details

```bash
GET /api/workflows/{workflow_name}
```

Returns complete workflow config including steps, execution config, and parameters.

### Validate Parameters

```bash
POST /api/workflows/{workflow_name}/validate
Content-Type: application/json

{
    "parameters": {
        "date_param": "250624",
        "submit_job": true
    }
}
```

## Executions & Logs

```bash
# Get execution records
GET /api/executions?task_id={task_id}

# Query system logs
GET /api/logs?task_id={task_id}&level=error
```

## File Downloads

### Download File

```bash
GET /api/downloads/{filename}
```

### Download Task Files

```bash
GET /api/downloads/task/{task_id}?file_type=merged_pdf&date=250519
```

Parameters:
- `file_type` (required): merged_pdf/log/output
- `date` (optional): Date parameter
- `step_id` (optional): Step ID

### List Available Files

```bash
GET /api/downloads/list?task_id=xxx&file_type=pdf
```

### Check File Exists

```bash
GET /api/downloads/check/{filename}
```

## Standard Workflow Steps

`topup_standard_workflow` consists of 5 steps:

1. **Step 0**: Get available dates
2. **Step 1.1**: First job submission
3. **Step 1.2**: Move files
4. **Step 1.3**: IST analysis
5. **Step 1.4**: Merge images

## Common Parameters

- `date_param`: Date in YYMMDD format (e.g., "250624")
- `submit_job`: Boolean, whether to submit jobs
- `max_wait_minutes`: Maximum wait time for job completion

## Error Handling

Tasks can fail due to:
- SSH connection issues (lxlogin.ihep.ac.cn, beslogin)
- Invalid parameters
- Timeout (default 30 minutes)
- Step execution errors

Check logs with `/api/tasks/{task_id}/logs` for debugging.

## Resources

See [references/endpoints.md](references/endpoints.md) for detailed API specification.
