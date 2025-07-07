# TickTick MCP Server
README: [English](README.md) | [中文](README_CN.md)
> 这篇文档由Claude翻译，部分翻译可能存在错误。

> **Credit**: 本项目部分功能/工具基于 [jacepark12/ticktick-mcp](https://github.com/jacepark12/ticktick-mcp) 的思路开发

一个用于 TickTick/滴答清单 待办事项集成的模型上下文协议 (MCP) 服务器。作为学习 MCP 的练习项目创建，同时解决实际需求 - 使用 AI 自动将复杂目标分解为可执行的任务。

## 🚀 改进功能
1. **自动化认证流程** - 浏览器自动打开进行 OAuth 认证，无需手动 CLI 操作
2. **扩展操作功能** - 新增子任务、任务过滤器和更多项目/任务属性
3. **AI 提示模板** - 为 Claude Desktop 包含实验性提示（通过 + → MCP Server → Prompt/References 访问）

## 📋 安装配置

### 1. 环境搭建
```bash
git clone https://github.com/Xrondev/mcp-dida365
cd mcp-dida365
uv sync
```

### 2. OAuth 配置
1. 在 [TickTick 开发者中心](https://developer.ticktick.com) 或 [滴答清单开发者中心（中国用户）](https://developer.dida365.com) 注册应用
2. **设置重定向 URI**: `http://localhost:11365/callback`
3. 记录您的 Client ID 和 Client Secret

### 3. 环境变量设置
```bash
cp .env.template .env
vim .env  # 编辑您的凭据
```

**滴答清单配置** (默认):
```env
TICKTICK_AUTH_URL=https://dida365.com/oauth/authorize
TICKTICK_TOKEN_URL=https://dida365.com/oauth/token
TICKTICK_API_BASE_URL=https://api.dida365.com
TICKTICK_CLIENT_ID=your_client_id
TICKTICK_CLIENT_SECRET=your_client_secret
TICKTICK_PORT=11365
TICKTICK_SCOPE="tasks:read tasks:write"
```

**TickTick 配置**: 将 URL 替换为 `ticktick.com` 域名

### 4. MCP 客户端配置
在您的 MCP 客户端（Claude Desktop, Cursor, Copilot 等）中，修改 mcp 配置文件。

```json
{
  "mcpServers": {
    // 您的其他 MCP 服务器 ...
    "ticktick-mcp": {
      "command": "/absolute/path/to/uv",
      "args": ["run", "--with", "mcp", "/absolute/path/to/main.py"]
    }
  }
}
```

**查找路径**:
```bash
# 首先激活虚拟环境
source .venv/bin/activate
which uv  # 获取 uv 路径
pwd       # 获取当前目录，追加 /main.py
```

## 🔐 身份认证
服务器在首次启动或令牌无效时会自动打开浏览器进行 OAuth 认证。令牌保存到 `.token` 文件，有效期为 **180 天**。

## ⚠️ 使用限制
1. **API 限制**:
   - ~~无法访问收集箱任务~~ [开发中] - 仅支持项目任务
   - 某些功能（高级过滤器、任务重复）不可用（或开发中）
   - 已完成任务在某些端点中不可见
   - **令牌 180 天后过期**（无刷新功能，因为端点未返回刷新令牌）

2. **实现说明**:
   - 由于 API 文档不明确，repeatFlag 和提醒等任务属性可能无效或行为异常

## 故障排除

**浏览器无法打开进行认证:**
- 检查端口 11365 是否可用，如需要可更改端口（记得同时在开发者中心更改回调 URL）
- 如需要可手动访问认证 URL（查看日志）

**"Token invalid" 错误:**
- 尝试删除 .token 文件并重新认证

**MCP 客户端问题:**
- 在配置中使用绝对路径
- 检查 main.py 是否有执行权限

其他问题：请提交 issue 并附上错误详情（mcp.log 或任何与服务器相关的日志）

## ⭐ 支持项目
如果这个项目对您有帮助，请给个 Star！

## 📄 许可证
MIT 许可证 - 详见 LICENSE 文件