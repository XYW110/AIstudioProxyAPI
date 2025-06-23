import asyncio
import json
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from datetime import datetime

# 创建一个 FastAPI 应用实例
app = FastAPI(
    title="MCP Helper Service",
    description="一个独立的外部 Helper 服务，用于扩展主程序功能并支持 MCP 协议。",
    version="1.0.0",
)

# =============================================================================
# MCP 工具函数模拟
# =============================================================================
def get_current_time_tool():
    """一个简单的工具函数，用于获取当前时间。"""
    return {
        "tool_name": "get_current_time",
        "result": {
            "time": datetime.now().isoformat(),
            "message": "这是从独立的 MCP Helper Service 的本地工具返回的时间。",
        }
    }

# MCP 工具注册表
MCP_TOOLS = {
    "get_current_time": get_current_time_tool,
}

# =============================================================================
# 流式响应生成器
# =============================================================================
async def mcp_tool_response_stream(tool_name: str):
    """
    为 MCP 工具调用的结果生成一个流式响应。
    """
    tool_func = MCP_TOOLS.get(tool_name)
    if not tool_func:
        response_data = {"error": f"Tool '{tool_name}' not found."}
    else:
        response_data = tool_func()

    # 将结果格式化为与主程序兼容的流式数据块
    yield f"data: {json.dumps(response_data)}\n\n"
    await asyncio.sleep(0.1) # 模拟网络延迟


async def forward_to_aistudio_stream(request: Request):
    """
    一个占位符函数，未来可以实现将请求转发到真正的 AI Studio。
    当前它只会返回一个表示未实现的消息。
    """
    sapisid = request.headers.get("X-Helper-SAPISID", "Not Provided")
    response_data = {
        "message": "请求已收到，但尚未实现转发到 AI Studio 的功能。",
        "sapisid_received": sapisid,
        "note": "这个响应来自于独立的 mcp_helper_service.py"
    }
    yield f"data: {json.dumps(response_data)}\n\n"


# =============================================================================
# API 端点
# =============================================================================
@app.post("/getStreamResponse")
async def get_stream_response(request: Request):
    """
    主程序调用的核心接口。
    它会解析请求，判断是需要调用 MCP 工具还是转发。
    """
    try:
        body = await request.json()
        messages = body.get("messages", [])
        last_message = messages[-1].get("content", "") if messages else ""

        # **MCP 逻辑判断**
        # 如果用户输入以 "mcp:" 开头，我们就认为它是一个工具调用指令
        if last_message.lower().startswith("mcp:"):
            tool_name = last_message.split(":")[1].strip()
            print(f"✅ 检测到 MCP 工具调用指令: {tool_name}")
            return StreamingResponse(mcp_tool_response_stream(tool_name), media_type="text/event-stream")

        # **默认行为**
        # 否则，我们执行默认行为（当前为占位符）
        print("➡️ 执行默认行为 (当前为占位符，未来可转发到 AI Studio)")
        return StreamingResponse(forward_to_aistudio_stream(request), media_type="text/event-stream")

    except Exception as e:
        print(f"❌ 处理请求时发生错误: {e}")
        async def error_stream():
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream", status_code=500)


@app.get("/")
def read_root():
    """根路径，用于健康检查。"""
    return {"status": "MCP Helper Service is running"}

# =============================================================================
# 服务启动
# =============================================================================
if __name__ == "__main__":
    # 在这里可以从 .env 文件或命令行参数读取端口号
    # 为了简单起见，我们先硬编码一个端口
    helper_port = 3121
    print(f"🚀 MCP Helper Service 将在 http://127.0.0.1:{helper_port} 上启动")
    uvicorn.run(app, host="127.0.0.1", port=helper_port)