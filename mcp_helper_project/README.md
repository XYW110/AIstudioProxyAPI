# MCP Helper Service

这是一个独立的外部 Helper 服务，旨在与 `AIStudioProxyAPI` 项目配合使用，为其提供可扩展的 MCP (Model Context Protocol) 功能。

## 🎯 功能

-   **提供 `/getStreamResponse` 接口**：与 `AIStudioProxyAPI` 的 Helper 模式完全兼容。
-   **MCP 指令支持**：可以拦截特定的用户指令（例如 `mcp:get_current_time`），并调用本地工具函数来处理，而不是将所有请求都发往 AI Studio。
-   **可扩展的工具集**：可以方便地在 `mcp_helper_service.py` 中添加更多的本地工具。
-   **独立部署**：作为一个独立的项目，它可以与主应用分开部署和管理。

## ⚙️ 安装

本项目使用 [Poetry](https://python-poetry.org/) 进行依赖管理。

1.  **进入项目目录**:
    ```bash
    cd mcp_helper_project
    ```

2.  **安装依赖**:
    Poetry 会自动创建虚拟环境并安装所需的库（FastAPI, Uvicorn）。
    ```bash
    poetry install
    ```

## 🚀 运行

可以直接通过 Python 运行主服务文件，或者使用 `poetry run` 在虚拟环境中运行。

```bash
# 激活虚拟环境后运行
python mcp_helper_service.py

# 或者直接使用 poetry run
poetry run python mcp_helper_service.py
```

服务将默认在 `http://127.0.0.1:3121` 上启动。

## 🔗 与主项目集成

1.  **启动本服务**：确保 `mcp_helper_service.py` 正在运行。
2.  **配置主项目**：
    在 `AIStudioProxyAPI` 项目的 `.env` 文件中，设置 `GUI_DEFAULT_HELPER_ENDPOINT`：
    ```ini
    GUI_DEFAULT_HELPER_ENDPOINT=http://127.0.0.1:3121/getStreamResponse
    ```
    或者，在启动 `AIStudioProxyAPI` 时使用命令行参数：
    ```bash
    python launch_camoufox.py --helper "http://127.0.0.1:3121/getStreamResponse"