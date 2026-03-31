# @Time    : 2026/3/31 11:30
# @Author  : hero
# @File    : mcp_stdio_client.py

import asyncio
from mcp.client.stdio import stdio_client

from mcp import ClientSession,StdioServerParameters



async def stdio_run():
    #tips stdio的客户端和服务端是同一台机器当中的两个进程，此时我们要通知客户端，服务端怎么启动起来
    server_params=StdioServerParameters(
        command='python',
        args=["./mcp_stdio_server.py"],  #tips:相当于命令行里 python mcp_stdio_server.py
    )
    async with stdio_client(server_params) as (read,write):
        async with ClientSession(read,write) as session:

            #tips:初始化链接
            await session.initialize()

            #tips 获取可用工具
            tools = await session.list_tools()
            print(tools)
            print()

            #tips 调用工具
            call_res=await session.call_tool("add",{'a':1,'b':9})
            print(call_res)



asyncio.run(stdio_run())