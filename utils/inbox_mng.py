import os
import json
from typing import Optional, Dict, Any

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".data")


def read_data() -> Dict[str, Any]:
    """Read the .data file and return its contents as a dict. If not exists, return empty dict."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return {}


def save_data(data: Dict[str, Any]) -> None:
    """Save the given dict to the .data file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_inbox_project_id(client: Any) -> Optional[str]:
    """
    Get the inbox project id, using .data cache if available, otherwise discover it via the workaround.
    `client` should be an instance of APIClient or compatible.
    """
    data = read_data()
    if "inbox_project_id" in data:
        return data["inbox_project_id"]

    # Workaround: create a task with an invalid project id
    invalid_project_id = "11365in"
    task = client.create_task(project_id=invalid_project_id, title="_inbox_id_probe_")
    if not isinstance(task, dict) or "projectId" not in task or "id" not in task:
        return None
    inbox_project_id = task["projectId"]
    task_id = task["id"]
    # Delete the probe task
    client.delete_task(inbox_project_id, task_id)
    # Save to .data
    data["inbox_project_id"] = inbox_project_id
    save_data(data)
    return inbox_project_id
