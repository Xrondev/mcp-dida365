import os
from dotenv import load_dotenv
import httpx
from utils.token_mng import load_token, is_token_valid
from utils.auth import Auth
from typing import Dict, List, Any, Literal, Optional, Callable
import logging
import json

load_dotenv()

ReturnType = Dict[Any, Any] | List[Dict[Any, Any]] | None


class APIClient:
    def __init__(self):
        if not is_token_valid():
            Auth().run()
        self.token, _ = load_token()
        self.base_url = os.getenv("TICKTICK_API_BASE_URL", "https://api.dida365.com")
        self.api_version = os.getenv("TICKTICK_API_VERSION", "/open/v1")

    def _prepare_fields(
        self, fields: dict[str, tuple[Any, Callable[[Any], Any] | None]]
    ):
        data: dict[str, Any] = {}
        for key, (val, fn) in fields.items():
            if val is None:
                continue
            data[key] = fn(val) if fn is not None else val
        return data

    def _make_request(self, method: str, url: str, **kwargs) -> ReturnType:
        """
        Make an authenticated request to the provider API.
        """

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        headers["User-Agent"] = "MCP-Dida365/1.0"

        response = httpx.request(
            method,
            f"{self.base_url}{self.api_version}{url}",
            headers=headers,
            json=kwargs.get("data", {}),  # well, json is a must.
        )
        try:
            response.raise_for_status()
            # Return empty dict for 204 No Content
            if response.status_code == 204 or response.text == "":
                return {}
            return response.json()
        except httpx.HTTPStatusError as e:
            logging.error(f"API Request Failed: {e}")
            return {"error": str(e)}

    # Project helper functions
    def get_projects(self) -> List[Any]:
        """
        Get all projects, return a list of projects
        """
        result = self._make_request("GET", "/project")
        if isinstance(result, list):
            return result
        else:
            return []

    def get_project_by_id(self, project_id: str) -> Dict[Any, Any]:
        """
        Get a project by id, return a dict
        """
        result = self._make_request("GET", f"/project/{project_id}")
        if isinstance(result, dict):
            return result
        else:
            return {}

    def get_project_details(self, project_id: str) -> Dict[Any, Any]:
        """
        Get a project data and tasks, return a dict
        """
        result = self._make_request("GET", f"/project/{project_id}/data")
        if isinstance(result, dict):
            return result
        else:
            return {}

    def create_project(
        self,
        name: str,
        color: Optional[str] = None,
        sortOrder: Optional[int] = None,
        viewMode: Optional[Literal["list", "kanban", "timeline"]] = None,
        kind: Optional[Literal["TASK", "NOTE"]] = None,
    ) -> Dict[Any, Any]:
        """
        Create a project, return a dict
        """
        fields = {
            "name": (name, str),
            "color": (color, None),
            "sortOrder": (sortOrder, str),
            "viewMode": (viewMode, None),
            "kind": (kind, None),
        }
        data = self._perpare_fields(fields)
        logging.info(f"Creating project: {json.dumps(data)}")
        result = self._make_request("POST", "/project", data=data)
        if isinstance(result, dict):
            return result
        else:
            return {"error": "Failed to create project"}

    def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        color: Optional[str] = None,
        sortOrder: Optional[int] = None,
        viewMode: Optional[Literal["list", "kanban", "timeline"]] = None,
        kind: Optional[Literal["TASK", "NOTE"]] = None,
    ) -> Dict[Any, Any]:
        """
        Update a project, return a dict
        """
        fields = {
            "name": (name, None),
            "color": (color, None),
            "sortOrder": (sortOrder, str),
            "viewMode": (viewMode, None),
            "kind": (kind, None),
        }
        data = self._perpare_fields(fields)
        result = self._make_request("PUT", f"/project/{project_id}", data=data)
        if isinstance(result, dict):
            return result
        else:
            return {"error": "Failed to update project"}

    def delete_project(self, project_id: str) -> ReturnType:
        """
        Delete a project, return a dict
        """
        return self._make_request("DELETE", f"/project/{project_id}")

    # Task helper functions
    def get_task_by_id(self, project_id: str, task_id: str) -> ReturnType:
        """
        Get task by project id and task id, return a dict or empty
        """
        return self._make_request("GET", f"/project/{project_id}/task/{task_id}")

    def create_task(
        self,
        project_id: str,
        title: str,
        content: Optional[str] = None,
        isAllDay: Optional[bool] = None,
        startDate: Optional[str] = None,
        dueDate: Optional[str] = None,
        timeZone: Optional[str] = None,
        reminders: Optional[list] = None,
        repeatFlag: Optional[str] = None,
        priority: Optional[int] = None,
        sortOrder: Optional[int] = None,
        items: Optional[list] = None,
    ) -> ReturnType:
        """
        Create a task in a project. Returns the created task dict.
        All parameters except project_id and title are optional and map to the API fields.
        """
        fields = {
            "projectId": (project_id, None),
            "title": (title, None),
            "content": (content, None),
            "isAllDay": (isAllDay, lambda x: str(x).lower()),
            "startDate": (startDate, None),
            "dueDate": (dueDate, None),
            "timeZone": (timeZone, None),
            "reminders": (reminders, None),
            "repeatFlag": (repeatFlag, None),
            "priority": (priority, None),
            "sortOrder": (sortOrder, None),
            "items": (items, lambda x: json.dumps(x)),
        }
        data = self._perpare_fields(fields)
        return self._make_request("POST", "/task", data=data)

    def update_task(
        self,
        task_id: str,
        project_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        isAllDay: Optional[bool] = None,
        startDate: Optional[str] = None,
        dueDate: Optional[str] = None,
        timeZone: Optional[str] = None,
        reminders: Optional[list] = None,
        repeatFlag: Optional[str] = None,
        priority: Optional[int] = None,
        sortOrder: Optional[int] = None,
        items: Optional[list] = None,
    ) -> ReturnType:
        """
        Update a task, return a dict
        """
        fields = {
            "id": (task_id, None),
            "projectId": (project_id, None),
            "title": (title, None),
            "content": (content, None),
            "isAllDay": (isAllDay, lambda x: str(x).lower()),
            "startDate": (startDate, None),
            "dueDate": (dueDate, None),
            "timeZone": (timeZone, None),
            "reminders": (reminders, None),
            "repeatFlag": (repeatFlag, None),
            "priority": (priority, None),
            "sortOrder": (sortOrder, None),
            "items": (items, lambda x: json.dumps(x)),
        }
        data = self._perpare_fields(fields)
        return self._make_request("PUT", f"/task/{task_id}", data=data)

    def complete_task(self, project_id: str, task_id: str) -> ReturnType:
        """
        Complete a task, return a dict
        """
        return self._make_request(
            "POST", f"/project/{project_id}/task/{task_id}/complete"
        )

    def delete_task(self, project_id: str, task_id: str) -> ReturnType:
        """
        Delete a task, return a dict
        """
        return self._make_request("DELETE", f"/project/{project_id}/task/{task_id}")
