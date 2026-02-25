import requests

url = "http://127.0.0.1:5000/api/tasks"  # 修改为实际的地址
payload = {
    "user_id": "user123",
    "workflow_name": "get_available_dates_workflow",
    "task_name": "获取可用日期列表",
    "parameters": {
        "include_processed": True,
        "user_id": "user123"
    }
}

resp = requests.post(url, json=payload)  # requests 会自动设置 Content-Type: application/json
print(resp.status_code, resp.text)