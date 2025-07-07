import os
from dotenv import load_dotenv
import httpx
from utils.token_mng import load_token, is_token_valid
from utils.auth import Auth
from typing import Dict, List, Any, Literal, Optional
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

    @staticmethod
    def _build_data(**kwargs):
        # Optionally accept a type_map for conversion
        type_map = kwargs.pop("_type_map", {})
        return {
            k: (type_map[k](v) if k in type_map and v is not None else v)
            for k, v in kwargs.items()
            if v is not None
        }

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
        data = self._build_data(
            name=name,
            color=color,
            sortOrder=sortOrder,
            viewMode=viewMode,
            kind=kind,
            _type_map={"name": str, "sortOrder": str},
        )
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
        data = self._build_data(
            name=name,
            color=color,
            sortOrder=sortOrder,
            viewMode=viewMode,
            kind=kind,
            _type_map={"sortOrder": str},
        )
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
        data = self._build_data(
            projectId=project_id,
            title=title,
            content=content,
            isAllDay=isAllDay,
            startDate=startDate,
            dueDate=dueDate,
            timeZone=timeZone,
            reminders=reminders,
            repeatFlag=repeatFlag,
            priority=priority,
            sortOrder=sortOrder,
            items=items,
        )
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
        data = self._build_data(
            id=task_id,
            projectId=project_id,
            title=title,
            content=content,
            isAllDay=isAllDay,
            startDate=startDate,
            dueDate=dueDate,
            timeZone=timeZone,
            reminders=reminders,
            repeatFlag=repeatFlag,
            priority=priority,
            sortOrder=sortOrder,
            items=items,
        )
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
