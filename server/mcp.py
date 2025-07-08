from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional, Literal
from server.client import APIClient
import logging
from utils.filter import filter_task
from datetime import datetime

mcp = FastMCP(
    "Dida365 MCP",
    instructions="""
This server provides a todo list management service for user.
If not specified, the task should always be created in the default project named "AI-Planner".
Prompt the user to re-auth when response contains unauthorized error.
""",
)
client = APIClient()


def format_task(task: Dict[Any, Any]) -> str:
    lines: List[str] = []

    # 1) Subtasks
    items = task.get("items") or []
    if items:
        lines.append("Subtasks:")
        for idx, sub in enumerate(items, 1):
            fields = "; ".join(
                f"{k}: {v}"
                for k, v in sub.items()
                if v not in (None, "", [], {}) and k != "timeZone"
            )
            lines.append(f"  {idx}. {fields}")

    # 2) Other task fields
    skip = {"items"}
    for k, v in task.items():
        if k in skip or v in (None, "", [], {}):
            continue
        lines.append(f"{k}: {v}")

    # 3) Add current time
    lines.append(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return "\n".join(lines)


def format_project(project: Dict[Any, Any]) -> str:
    return "\n".join(
        f"{k}: {v}" for k, v in project.items() if v not in (None, "", [], {})
    )


@mcp.prompt()
def generate_new_task_request(task_description: str) -> str:
    """
    Generate a new user message for new task(s).
    """
    return f"""Use the MCP, create new task(s) with the following description: {task_description}. 
You should split the task into subtasks(capstones) and fill the details for the task. If the subtask items are supposed to have due date, create it as a Task.
The task should have a appropriate due date. Take other tasks in the week into consideration.
"""


@mcp.tool()
def get_projects() -> str:
    """
    Get a list of all Projects(collections of tasks). The inbox contains all tasks that are not allocated to any project.

    Returns:
        str: Formatted list of projects
    """
    try:
        projects = client.get_projects()
        projects = list(filter(lambda x: not x.get("closed"), projects))
        formatted = []
        if projects:
            for k, v in enumerate(projects, 1):
                formatted.append(f"{k}. {format_project(v)}")
        return "\n\n".join(formatted)
    except Exception as e:
        logging.error(f"Error in get_projects: {e}")
        return f"Error in get_projects: {e}"


@mcp.tool()
def get_project_by_id(project_id: str) -> str:
    """
    get a project details by id, no tasks included.

    Args:
        project_id (str): The ID of the project to get details for.

    Returns:
        str: Formatted single project details
    """
    try:
        project = client.get_project_by_id(project_id)
        return format_project(project)
    except Exception as e:
        logging.error(f"Error in get_project_by_id: {e}")
        return f"Error in get_project_by_id: {e}"


@mcp.tool()
def get_project_details(project_id: str) -> str:
    """
    Get a project(collections of tasks) details and a list of tasks in the project.
    Note the tasks might be very long, use filter_project_tasks to filter out the task you need.

    Args:
        project_id (str): The ID of the project to get details for.

    Returns:
        str: Formatted single project details and tasks in the project.
    """
    try:
        details = client.get_project_details(project_id)
        formatted = []
        if details:
            formatted.append("Project Details:")
            project = details.get("project", {})
            tasks = details.get("tasks", [])
            formatted.append(format_project(project))
            formatted.append("Tasks:")
            for idx, task in enumerate(tasks, 1):
                formatted.append(f"{idx}. {format_task(task)}")
        return "\n\n".join(formatted)
    except Exception as e:
        logging.error(f"Error in get_project_details: {e}")
        return f"Error in get_project_details: {e}"


@mcp.tool()
def filter_project_tasks(project_id: str, filter_fields: List[str]) -> str:
    """
    Filter the tasks in a project.
    Return only those tasks for which **all** filter expressions match.

    filter_fields is a list of strings, note "==" is used for absolutely equal, not recommended for date fields,
    literal date indicator only has today, tomorrow, yesterday.
    priority has high, medium, low, none.
     e.g.
      ["dueDate <= tomorrow(or iso format date)",
       "startDate <= today(or iso format date)",
       "priority >= high(or low, medium, none)"]

    Args:
        project_id (str): The ID of the project to filter tasks for.
        filter_fields (List[str]): The fields to filter the tasks by.

    Returns:
        str: Formatted list of filtered tasks
    """
    try:
        tasks = client.get_project_details(project_id).get("tasks", [])
        filtered = filter_task(tasks, filter_fields)
        formatted = []
        if filtered:
            for task in filtered:
                formatted.append(format_task(task))
        return "\n\n".join(formatted)
    except Exception as e:
        logging.error(f"Error in filter_project_tasks: {e}")
        return f"Error in filter_project_tasks: {e}"


@mcp.tool()
def create_project(
    name: str,
    color: Optional[str] = None,
    sortOrder: Optional[int] = None,
    viewMode: Optional[Literal["list", "kanban", "timeline"]] = "list",
    kind: Optional[Literal["TASK", "NOTE"]] = None,
) -> str:
    """
    Create a project(collection of tasks).

    Args:
        name (str): The name of the project.
        color (str): The color of the project, hex color code start with #. Optional.
        sortOrder (int): The sort order of the project. Optional
        viewMode (str): The view mode of the project. Options: list, kanban, timeline. Optional
        kind (str): The kind of the project. Options: TASK, NOTE. Optional

    Returns:
        str: Formatted single project details
    """
    try:
        project = client.create_project(
            name,
            color=color,
            sortOrder=sortOrder,
            viewMode=viewMode,
            kind=kind,
        )
        return format_project(project)
    except Exception as e:
        logging.error(f"Error in create_project: {e}")
        return f"Error in create_project: {e}"


@mcp.tool()
def update_project(
    project_id: str,
    name: Optional[str] = None,
    color: Optional[str] = None,
    sortOrder: Optional[int] = None,
    viewMode: Optional[Literal["list", "kanban", "timeline"]] = None,
    kind: Optional[Literal["TASK", "NOTE"]] = None,
) -> str:
    """
    Update a project(collection of tasks).

    Args:
        project_id (str): The ID of the project to update.
        name (str): The name of the project. Optional
        color (str): The color of the project, hex color code start with #. Optional
        sortOrder (int): The sort order of the project. Optional
        viewMode (str): The view mode of the project. Options: list, kanban, timeline. Optional
        kind (str): The kind of the project. Options: TASK, NOTE. Optional
    """
    try:
        project = client.update_project(
            project_id,
            name=name,
            color=color,
            sortOrder=sortOrder,
            viewMode=viewMode,
            kind=kind,
        )
        return format_project(project)
    except Exception as e:
        logging.error(f"Error in update_project: {e}")
        return f"Error in update_project: {e}"


@mcp.tool()
def delete_project(project_id: str) -> str:
    """
    Delete a project(collection of tasks).
    """
    try:
        client.delete_project(project_id)
        return f"Project {project_id} deleted successfully"
    except Exception as e:
        logging.error(f"Error in delete_project: {e}")
        return f"Error in delete_project: {e}"


@mcp.tool()
def get_task_by_id(project_id: str, task_id: str) -> str:
    """
    Get a task by id.
    """
    try:
        task = client.get_task_by_id(project_id, task_id)
        if isinstance(task, dict):
            return format_task(task)
        else:
            return f"Task {task_id} not found"
    except Exception as e:
        logging.error(f"Error in get_task_by_id: {e}")
        return f"Error in get_task_by_id: {e}"


@mcp.tool()
def create_task(
    project_id: str,
    title: str,
    content: Optional[str] = None,
    isAllDay: Optional[bool] = None,
    startDate: Optional[str] = None,
    dueDate: Optional[str] = None,
    repeatFlag: Optional[str] = None,
    priority: Optional[int] = None,
    sortOrder: Optional[int] = None,
    items: Optional[list] = None,
) -> str:
    """
    Create a task in a project.

    Args:
        project_id (str): The ID of the project to create the task in.
        title (str): The title of the task, keep it short and concise.
        content (str): The content/details of the task. Optional
        isAllDay (bool): Whether the task is all day. Optional
        startDate (str): The start date of the task. Optional. Example : "2019-11-13T03:00:00+0000"
        dueDate (str): The due date of the task. Optional. Example : "2019-11-13T03:00:00+0000"
        repeatFlag (str): The repeat pattern of the task. Optional. Example: "RRULE:FREQ=DAILY;INTERVAL=1
        priority (int): The priority of the task. Optional. 0: none, 1:low, 3:medium, 5:high
        sortOrder (int): Smaller int will be at the top. Optional.
        items (list): The items(subtasks/capstones) of the task. Optional, do NOT wrap the items as a string. Example: [{
                    "title": "Subtask 1",
                },{
                    "title": "Subtask 2",
                }]

    Returns:
        str: Formatted single task details
    """
    try:
        task = client.create_task(
            project_id,
            title,
            content=content,
            isAllDay=isAllDay,
            startDate=startDate,
            dueDate=dueDate,
            repeatFlag=repeatFlag,
            priority=priority,
            sortOrder=sortOrder,
            items=items,
        )
        if isinstance(task, dict):
            return format_task(task)
        else:
            return f"Error in create_task: {task}"
    except Exception as e:
        logging.error(f"Error in create_task: {e}")
        return f"Error in create_task: {e}, {items}"


@mcp.tool()
def update_task(
    task_id: str,
    project_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    isAllDay: Optional[bool] = None,
    startDate: Optional[str] = None,
    dueDate: Optional[str] = None,
    repeatFlag: Optional[str] = None,
    priority: Optional[int] = None,
    sortOrder: Optional[int] = None,
    items: Optional[list] = None,
) -> str:
    """
    Update a task.

    Args:
        task_id (str): The ID of the task to update.
        project_id (str): The ID of the project to update the task in.
        title (str): The title of the task. Optional
        content (str): The content of the task. Optional
        isAllDay (bool): Whether the task is all day. Optional
        startDate (str): The start date of the task. Optional
        dueDate (str): The due date of the task. Optional
        repeatFlag (str): The repeat pattern of the task. Optional. Example: "RRULE:FREQ=DAILY;INTERVAL=1
        priority (int): The priority of the task. Optional. 0: none, 1:low, 3:medium, 5:high
        sortOrder (int): Smaller int will be at the top. Optional.
        items (list): The items(subtasks/capstones) of the task. Optional. Example: [{
                    "title": "Subtask 1",
                },{
                    "title": "Subtask 2",
                }]
    """
    try:
        task = client.update_task(
            task_id,
            project_id,
            title=title,
            content=content,
            isAllDay=isAllDay,
            startDate=startDate,
            dueDate=dueDate,
            repeatFlag=repeatFlag,
            priority=priority,
            sortOrder=sortOrder,
            items=items,
        )
        if isinstance(task, dict):
            return format_task(task)
        else:
            return f"Error in update_task: {task_id}, check id and project_id"
    except Exception as e:
        logging.error(f"Error in update_task: {e}")
        return f"Error in update_task: {e}, {items}"


@mcp.tool()
def complete_task(project_id: str, task_id: str) -> str:
    """
    Complete a task.
    """
    try:
        client.complete_task(project_id, task_id)
        return f"Task {task_id} completed successfully"
    except Exception as e:
        logging.error(f"Error in complete_task: {e}")
        return f"Error in complete_task: {e}"


@mcp.tool()
def delete_task(project_id: str, task_id: str) -> str:
    """
    Delete a task.
    """
    try:
        client.delete_task(project_id, task_id)
        return f"Task {task_id} deleted successfully"
    except Exception as e:
        logging.error(f"Error in delete_task: {e}")
        return f"Error in delete_task: {e}"
