# TickTick MCP Server
README: [English](README_EN.md) | [中文](README.md)
> **Credits**: This project builds upon ideas from [jacepark12/ticktick-mcp](https://github.com/jacepark12/ticktick-mcp)

A Model Context Protocol (MCP) server for TickTick/Dida365 todo list integration. Created as a learning exercise for MCP while solving a real need - using AI to automatically decompose complex goals into actionable tasks.

## 🚀 Improvements

1. **Automated auth flow** - Browser automatically opens for OAuth, no manual CLI operations needed
2. **Expanded operations** - Added subtasks, task filters, and more attributes for projects/tasks
3. **Inbox tasks management** - Implemented a workround to manage the tasks inside the Inbox!
4. **AI prompt template** - Experimental prompt included for Claude Desktop (access via + → MCP Server → Prompt/References)

## 📋 Installation

### 1. Setup
```bash
git clone https://github.com/Xrondev/mcp-dida365
cd mcp-dida365
uv sync
```

### 2. OAuth Configuration

1. Register application at [TickTick Developer Center](https://developer.ticktick.com) or [Dida365 Developer Center (Chinese User)](https://developer.dida365.com)
2. **Set redirect URI**: `http://localhost:11365/callback`
3. Note your Client ID and Client Secret

### 3. Environment Setup
```bash
cp .env.template .env
vim .env  # Edit with your credentials
```

**For Dida365** (default):
```env
TICKTICK_AUTH_URL=https://dida365.com/oauth/authorize
TICKTICK_TOKEN_URL=https://dida365.com/oauth/token
TICKTICK_API_BASE_URL=https://api.dida365.com

TICKTICK_CLIENT_ID=your_client_id
TICKTICK_CLIENT_SECRET=your_client_secret
TICKTICK_PORT=11365
TICKTICK_SCOPE="tasks:read tasks:write"
```

**For TickTick**: Replace URLs with `ticktick.com` domains

### 4. MCP Client Configuration
In your MCP client(Claude Desktop, Cursor, Copilot, etc.), modify the mcp config file.
```json
{
  "mcpServers": {
    // YOUR OTHER MCP SERVERS ...
    "ticktick-mcp": {
      "command": "/absolute/path/to/uv",
      "args": ["run", "--with", "mcp", "/absolute/path/to/main.py"]
    }
  }
}
```

**Finding paths**:
```bash
# Activate venv first
source .venv/bin/activate
which uv  # Get uv path
pwd       # Get current directory, append /main.py
```

## 🔐 Authentication

The server automatically opens your browser for OAuth when first initiated or token no longer valid. Token is saved to `.token` file and valid for **180 days**.

## ⚠️ Limitations

1. **API Limitations**:
   - ~~Cannot access Inbox tasks, only project tasks~~ Solved
   - Some features (advanced filters, complex repeats) unavailable (or WIP)
   - Completed tasks not visible in some endpoints
   - **Tokens expire after 180 days** (no refresh available, as the endpoint did not return refresh token)

2. **Implementation Notes**:
   - Task attributes like repeatFlag and reminders may not available or behave unexpectedly due to unclear API docs
## Troubleshooting
**Browser doesn't open for auth:**

- Check if port 11365 is available, you can change port if needed (remember also change the CALLBACK URL in developer center)
- Manually visit the auth URL if needed (check logs)

**"Token invalid" errors:**

- Try delete .token file and re-authenticate

**MCP client issues:**

- Use absolute paths in configuration
- Check main.py has execute permissions

Other issues: Please open an issue with error details (mcp.log or any log you have that is related to the server)

## ⭐ Support
Star if this project helps! 

## 📄 License

MIT License - see LICENSE file for details.
