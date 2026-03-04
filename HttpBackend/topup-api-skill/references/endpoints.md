# Topup API Endpoints Reference

## Base URL

```
http://0.0.0.0:5000
```

## Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Service health status and version |

## Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tasks` | Create new task |
| GET | `/api/tasks` | List tasks (requires user_id) |
| GET | `/api/tasks/{task_id}` | Get task details |
| GET | `/api/tasks/{task_id}/progress` | Get task progress |
| POST | `/api/tasks/{task_id}/start` | Start task |
| POST | `/api/tasks/{task_id}/pause` | Pause task |
| POST | `/api/tasks/{task_id}/resume` | Resume task |
| POST | `/api/tasks/{task_id}/cancel` | Cancel task |
| GET | `/api/tasks/{task_id}/logs` | Get task logs |

### Create Task Request Body

```json
{
    "user_id": "string (required)",
    "workflow_name": "string (required)",
    "task_name": "string (optional)",
    "parameters": {
        "date_param": "YYMMDD format",
        "submit_job": "boolean",
        "max_wait_minutes": "integer"
    }
}
```

### List Tasks Query Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| user_id | Yes | - | User identifier |
| status | No | - | Filter by status |
| limit | No | 10 | Max results |
| offset | No | 0 | Pagination offset |

### Task Status Values

- `pending` - Task created, not started
- `running` - Task in progress
- `completed` - Task finished successfully
- `failed` - Task failed
- `cancelled` - Task cancelled by user

### Task Logs Query Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| level | No | - | info/warning/error/debug |
| limit | No | 100 | Max log entries |

## Workflows

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/workflows` | List all workflows |
| GET | `/api/workflows/{workflow_name}` | Get workflow details |
| POST | `/api/workflows/{workflow_name}/validate` | Validate parameters |

### Available Workflows

**topup_standard_workflow**
- Full Topup data processing pipeline
- Steps: get_dates → job_submission → move_files → ist_analysis → merge_images

**get_available_dates**
- Single step workflow to retrieve available dates

### Validate Request Body

```json
{
    "parameters": {
        "date_param": "250624",
        "submit_job": true
    }
}
```

## Executions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/executions` | Get step execution records |

### Query Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| task_id | Yes | Task identifier |

## Logs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/logs` | Query system logs |

### Query Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| task_id | No | Filter by task |
| level | No | Filter by log level |

## Downloads

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/downloads/{filename}` | Download file by name |
| GET | `/api/downloads/task/{task_id}` | Download task file |
| GET | `/api/downloads/list` | List available files |
| GET | `/api/downloads/check/{filename}` | Check file exists |

### Task Download Query Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| file_type | Yes | merged_pdf/log/output |
| date | No | Date parameter |
| step_id | No | Step identifier |

### List Files Query Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| task_id | No | Filter by task |
| file_type | No | Filter by type (e.g., pdf) |

## Response Formats

### Success Response

```json
{
    "success": true,
    "data": { ... },
    "message": "Operation completed"
}
```

### Error Response

```json
{
    "success": false,
    "error": "Error description",
    "message": "Human readable message"
}
```

## Configuration

Default settings (configurable via environment):

| Setting | Default | Description |
|---------|---------|-------------|
| MAX_PARALLEL_TASKS | 3 | Concurrent task limit |
| DEFAULT_TIMEOUT_MINUTES | 30 | Task timeout |
| MAX_RETRY_ATTEMPTS | 3 | Retry count on failure |
| RETRY_DELAY_SECONDS | 60 | Delay between retries |
| STEP_CHECK_INTERVAL | 5 | Status check interval (seconds) |
