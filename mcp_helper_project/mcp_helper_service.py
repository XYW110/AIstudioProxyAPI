import asyncio
import json
import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from datetime import datetime

# =============================================================================
# 日志系统配置
# =============================================================================
# 1. 创建一个 logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 2. 创建一个 handler，用于写入日志文件
# 使用 'utf-8' 编码以确保中文字符正确记录
file_handler = logging.FileHandler('app.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

# 3. 创建一个 handler，用于将日志输出到控制台
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 4. 定义 handler 的输出格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 5. 给 logger 添加 handler
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 禁用 uvicorn 的默认访问日志，以避免与我们的日志重复
logging.getLogger("uvicorn.access").disabled = True


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
    logger.info(f"准备调用 MCP 工具: {tool_name}")
    tool_func = MCP_TOOLS.get(tool_name)
    if not tool_func:
        logger.warning(f"请求的 MCP 工具 '{tool_name}' 未找到。")
        response_data = {"error": f"Tool '{tool_name}' not found."}
    else:
        logger.info(f"成功调用 MCP 工具: {tool_name}")
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
    logger.info(f"收到来自 {request.client.host} 的新请求。")
    try:
        body = await request.json()
        messages = body.get("messages", [])
        last_message = messages[-1].get("content", "") if messages else ""

        # **MCP 逻辑判断**
        # 如果用户输入以 "mcp:" 开头，我们就认为它是一个工具调用指令
        if last_message.lower().startswith("mcp:"):
            tool_name = last_message.split(":")[1].strip()
            logger.info(f"[OK] 检测到 MCP 工具调用指令: {tool_name}")
            return StreamingResponse(mcp_tool_response_stream(tool_name), media_type="text/event-stream")

        # **默认行为**
        # 否则，我们执行默认行为（当前为占位符）
        logger.info("--> 执行默认行为 (当前为占位符，未来可转发到 AI Studio)")
        return StreamingResponse(forward_to_aistudio_stream(request), media_type="text/event-stream")

    except Exception as e:
        # 使用 exc_info=True 来记录完整的异常堆栈信息
        logger.error(f"[ERROR] 处理请求时发生严重错误: {e}", exc_info=True)
        async def error_stream():
            yield f"data: {json.dumps({'error': 'An internal server error occurred.'})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream", status_code=500)


@app.get("/")
def read_root():
    """根路径，用于健康检查。"""
    logger.info("[OK] 健康检查端点 '/' 被调用。")
    return {"status": "MCP Helper Service is running"}

# =============================================================================
# 服务启动
# =============================================================================
if __name__ == "__main__":
    # 在这里可以从 .env 文件或命令行参数读取端口号
    # 为了简单起见，我们先硬编码一个端口
    helper_port = 3121
    logger.info(f"--> MCP Helper Service 即将在 http://127.0.0.1:{helper_port} 上启动...")
    uvicorn.run(app, host="127.0.0.1", port=helper_port)