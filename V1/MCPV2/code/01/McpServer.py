# @Time    : 2026/3/31 16:13
# @Author  : hero
# @File    : McpServer.py

import json
import httpx
import os
from mcp.server import FastMCP
from loguru import logger
from dotenv import load_dotenv
load_dotenv()

#创建FastMCP实例,用于启动天气服务端MCP服务
#一个mcpserver对外暴露多个，一系列TOOLCALLING工具类的集合
mcp=FastMCP(name='WeatherServerSSE',host='0.0.0.0',port=8888)

@mcp.tool()
def get_weather(city:str) ->str:
    """
    查询指定城市天气的即时天气信息
    参数:city:城市英文名，如Beijing
    返回:OpenWeather API的JSON字符串

    """
    url='https://api.openweathermap.org/data/2.5/weather'
    params={
        'q':city,
        'appid':os.getenv('OPENWEATHER_API_KEY'),
        'units':'metric',
        'lang':'zh-CN'
    }
    resp = httpx.get(url=url,params=params,timeout=10)
    data=resp.json()

    logger.info(f'查询{city}天气结果:{data}')
    return json.dumps(data,ensure_ascii=False)


if __name__ == '__main__':
    logger.info('启动MCP SSE天气服务器,监听http://0.0.0.0:8888/sse')

    #tips:运行MCP客户端,使用Server-Sent Events(SSE)作为传输协议
    mcp.run(transport='sse')