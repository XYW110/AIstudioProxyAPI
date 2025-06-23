# -*- coding: utf-8 -*-
"""
用于对 mcp_helper_service.py 进行压力测试的脚本。
旨在通过发送各种类型的请求来找出潜在的闪退原因。
"""
import requests
import json

# 服务运行的地址
BASE_URL = "http://127.0.0.1:3121"
# 通用的 /getStreamResponse 端点
STREAM_URL = f"{BASE_URL}/getStreamResponse"

def print_test_header(title: str):
    """打印一个漂亮的测试用例标题"""
    print("\n" + "="*50)
    print(f"--- {title} ---")
    print("="*50)

def print_request_info(method: str, url: str, headers: dict = None, payload=None):
    """打印请求的详细信息"""
    print(f"--> 发送请求: {method} {url}")
    if headers:
        print(f"    Headers: {json.dumps(headers)}")
    if payload:
        # 根据 payload 类型选择不同的打印方式
        if isinstance(payload, bytes):
            # 如果是 bytes，先解码再打印
            print(f"    Body: {payload.decode('utf-8', errors='ignore')}")
        elif isinstance(payload, str):
            # 如果是 str，直接打印
            print(f"    Body: {payload}")
        else:
            # 其他情况（如 dict），使用 json.dumps 美化
            print(f"    Body: {json.dumps(payload, ensure_ascii=False)}")

def print_response_info(response: requests.Response):
    """打印响应的详细信息"""
    print(f"<-- 收到响应: {response.status_code} {response.reason}")
    try:
        # 尝试以 JSON 格式打印响应体，如果失败则以文本格式打印
        print(f"    Content: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except json.JSONDecodeError:
        print(f"    Content: {response.text}")
    except Exception as e:
        print(f"    解析响应时出错: {e}")


def run_test(title, method, url, headers=None, data=None, json_payload=None):
    """
    一个通用的测试执行函数，封装了打印和请求逻辑。
    """
    print_test_header(title)
    
    # 确定 payload 用于日志打印
    log_payload = data if data is not None else json_payload
    print_request_info(method, url, headers, log_payload)

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            json=json_payload,
            timeout=10 # 设置10秒超时
        )
        print_response_info(response)
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {e}")


if __name__ == "__main__":
    print("开始对 mcp_helper_service.py 进行压力测试...")

    # 1. 健康检查
    run_test(
        title="测试用例 1: 健康检查",
        method="GET",
        url=BASE_URL + "/"
    )

    # 2. 正常工具调用
    run_test(
        title="测试用例 2: 正常工具调用 (get_current_time)",
        method="POST",
        url=STREAM_URL,
        headers={"Content-Type": "application/json"},
        json_payload={"messages": [{"content": "mcp:get_current_time"}]}
    )

    # 3. 无效工具调用
    run_test(
        title="测试用例 3: 调用不存在的工具",
        method="POST",
        url=STREAM_URL,
        headers={"Content-Type": "application/json"},
        json_payload={"messages": [{"content": "mcp:non_existent_tool"}]}
    )

    # 4. 非 JSON 请求体
    run_test(
        title="测试用例 4: 发送非 JSON 请求体",
        method="POST",
        url=STREAM_URL,
        headers={"Content-Type": "application/json"},
        data='"this is not a json string"'.encode('utf-8') # 确保发送原始字符串
    )

    # 5. 空消息列表
    run_test(
        title="测试用例 5: 发送空消息列表",
        method="POST",
        url=STREAM_URL,
        headers={"Content-Type": "application/json"},
        json_payload={"messages": []}
    )

    # 6. 格式错误的消息
    run_test(
        title="测试用例 6: 发送格式错误的消息",
        method="POST",
        url=STREAM_URL,
        headers={"Content-Type": "application/json"},
        json_payload={"messages": ["just a string"]}
    )

    print("\n" + "="*50)
    print("--- 所有测试用例执行完毕！请检查上面的输出。 ---")
    print("="*50)