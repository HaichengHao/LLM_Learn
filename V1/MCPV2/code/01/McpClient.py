# @Time    : 2026/3/31 16:13
# @Author  : hero
# @File    : McpClient.py

import asyncio
import json
import os
from typing import Any,Dict
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor,create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_mcp_adapters.client import MultiServerMCPClient
from loguru import logger
from dotenv import load_dotenv
load_dotenv()

#tips:加载服务器配置,其实就是简单的读取一下mcp.json并将其中反序列化(即转换为python字典格式)
def load_server_config(file_path:str='mcp.json')->Dict[str,Any]:
    """
    从指定的JSON文件中加载MCP服务器配置
    参数:
        file_path(str):配置文件路径,默认为mcp.json
    返回:
        Dict[str,Any]:包含MCP服务器配置的字典,若文件中没有"mcpServers"键则返回空字典
    """
    with open(file_path,'r',encoding='utf-8') as file:
        data=json.load(file) #tips:反序列化,将json转化为python的字典
        return data.get("mcpServers",{})


async def run_chat_loop()->None:
    """
    启动并运行一个基于MCP工具的聊天代理循环
    该函数会：
    1.加载MCP服务器配置
    2.初始化MCP客户端并获取工具
    3.创建基于openai的语言模型和代理
    4.启动命令行聊天循环
    5.在退出时清理资源
    返回:None
    """
    #加载服务器配置,tips 也就是拿到json
    server_config=load_server_config()
    #初始化mcp客户端并获取工具
    mcp_client=MultiServerMCPClient(server_config) #tips 也就是传进去配置字典
    tools=await mcp_client.get_tools() #tips:加载tool
    logger.info(f"已加载{len(tools)}个MCP工具:{[t.name for t in tools]}")

    #初始化语言模型、提示模板和代理执行器
    # llm=init_chat_model(
    #     model="gpt-4o-mini",
    #     api_key=os.getenv('api_key'),
    #     base_url=os.getenv('base_url')
    # )

    llm=ChatOpenAI(
        model='gpt-4o-mini',
        api_key=os.getenv('api_key'),
        base_url=os.getenv('base_url')
    )

    prompt=ChatPromptTemplate.from_messages(
        [
            ('system',"你是一个有用的助手,需要使用提供的工具来完成用户请求"),
            ('user',"{input}"),
            MessagesPlaceholder(
                variable_name="agent_scratchpad"
            ),
        ]
    )

    agent=create_openai_tools_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    agent_executor=AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors="解析用户请求失败,请重新输入清晰的指令"
    )

    #tips:对话开始聊天
    print("\n🤖MCP Agent已启动,请输入一个提问给(LLM+MCP)，输入'quit'退出")
    while True:
        user_input = input('\n你:').strip()
        if user_input.lower() == 'quit':
            break
        try:
            result = await agent_executor.ainvoke({'input':user_input})
            print(f'🤖:{result["output"]}')
        except Exception as e:
            logger.error(f'\n⚠️出错了:{e}')

    #tips:清理
    logger.info("🧹会话已结束,Bye")
if __name__ == '__main__':
    asyncio.run(run_chat_loop())