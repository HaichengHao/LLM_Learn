# @Time    : 2026/11/19 21:37
# @Author  : hero
# @File    : 00简单使用本地浏览器.py
import asyncio
import os

from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain_stagehand import StagehandMiddleware
from stagehand import Stagehand,local_browser
from langchain.chat_models import init_chat_model

load_dotenv()
MINIMAXKEY = os.getenv('MINIMAX_APIKEY')
Minimax_url=os.getenv('MINIMAX_URL')
model_name = os.getenv('MINIMAX_MODEL')

model = init_chat_model(
    model_provider="openai",
    api_key=MINIMAXKEY,
    base_url=Minimax_url,
    model=model_name
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
async def main():
    #启动本地chrome
    browser = await local_browser.launch(headless=False,executable_path="/usr/bin/google-chrome")

    try:
        #创建stagehand客户端
        stagehand = await Stagehand.create(browser=browser)
        agent = create_deep_agent(
            model=model,
            tools=[],
            middleware=[
                StagehandMiddleware(stagehand=stagehand)
            ],
            system_prompt=(
                "You are a browser automation assistant. "
                "Use the browser tools to navigate websites. "
                "Never claim to have visited a website unless "
                "you actually used the browser tools."
            )
        )

        #执行浏览器任务
        result = await agent.ainvoke({
            "messages":[
                {
                    "role":"user",
                    "content":(
                        "Use the browser tools to navigate to "
                        "https://news.ycombinator.com,"
                        "Read the titles of the top three stories "
                        "and summarize them in Chinese."
                    )

                }
            ]
        })

        # print(result["messages"][-1].content)
        # 输出完整执行过程
        for msg in result["messages"]:
            print(f"\n[{msg.type}]")

            if getattr(msg, "tool_calls", None):
                print("工具调用:", msg.tool_calls)

            if msg.content:
                print("内容:", str(msg.content)[:2000])
    finally:
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
