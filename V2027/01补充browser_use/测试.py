# @Time    : 2026/11/19 22:23
# @Author  : hero
# @File    : 测试.py

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()

# 1. 初始化 MiniMax
model = init_chat_model(
    model_provider="openai",
    api_key=os.getenv("MINIMAX_APIKEY"),
    base_url=os.getenv("MINIMAX_URL"),
    model=os.getenv("MINIMAX_MODEL"),
    temperature=0,
)
# model = init_chat_model(
#     model_provider="openai",
#     api_key=os.getenv("MINIMAX_APIKEY"),
#     base_url="https://api.minimaxi.com/v1",
#     model="MiniMax-M2.5",
#     temperature=0,
#     timeout=30,
#     max_retries=0,
# )


# 2. 定义测试工具
@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气信息。"""
    print(f"\n[工具执行] get_weather(city={city})")
    return f"{city}当前天气：晴天，温度25摄氏度。"


@tool
def calculator(a: int, b: int) -> int:
    """计算两个整数的乘积。"""
    print(f"\n[工具执行] calculator(a={a}, b={b})")
    return a * b


# 3. 绑定工具
tools = [get_weather, calculator]
tool_map = {t.name: t for t in tools}
llm_with_tools = model.bind_tools(tools)


def main():
    messages = [
        HumanMessage(
            content="请查询北京的天气，并计算123乘以456。"
        )
    ]

    # 最多执行5轮工具调用
    for i in range(5):
        print(f"\n========== 第{i + 1}轮 ==========")

        response = llm_with_tools.invoke(messages)
        messages.append(response)

        print("模型回复:", response.content)
        print("Tool Calls:", response.tool_calls)

        if response.invalid_tool_calls:
            print("无效工具调用:", response.invalid_tool_calls)
            break

        # 如果没有工具调用，说明模型已完成回答
        if not response.tool_calls:
            print("\n最终回答：", response.content)
            break

        # 4. 执行所有工具调用
        for call in response.tool_calls:
            name = call["name"]
            args = call["args"]

            print(f"\n调用工具: {name}")
            print(f"参数: {args}")

            if name not in tool_map:
                result = f"未知工具: {name}"
            else:
                try:
                    result = tool_map[name].invoke(args)
                except Exception as e:
                    result = f"工具执行失败: {e}"

            print("工具结果:", result)

            # 5. 将工具执行结果传回模型
            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=call["id"]
                )
            )
    else:
        print("\n达到最大调用轮数，测试结束。")


if __name__ == "__main__":
    main()
