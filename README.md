# Ticktick MCP Server
This project has code / ideas from [credit: jacepark12/ticktick-mcp](https://github.com/jacepark12/ticktick-mcp)  
I "invented wheels" as I am learning MCP. Some improvements were made during implementation.
## Improvements
1. More automated auth flow. No explicit `uv run` required anymore (mcp configure still needed)
2. Expanded operations on projects/tasks provided.

## Limitation
The limitation of the implementation including:
1. Due to the functionality limitation of current version of API, 
    1. you CANNOT R/W the tasks in the Inbox. You can only R/W the tasks in the Project (Lists).
    2. you might find some functionalities (e.g. filters, advanced repeat of task) is not available for MCP.
    3. completed tasks are not visible in some endpoint.
2. According to API docs and returning response of the OAuth. The token cannot be refreshed and only validate for 180 days.

## License
This project is licensed under the MIT License - see the LICENSE file for details.