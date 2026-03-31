# @Time    : 2026/3/31 11:31
# @Author  : hero
# @File    : mcp_stdio_server.py

'''
uv add mcp 需要装这个包
'''

from mcp.server.fastmcp import FastMCP

#tips:创建mcp实例

fastmcp_instance=FastMCP('Demo')

#tips:为实例添加工具

@fastmcp_instance.tool()
def add(a:int,b:int)->int:
    return a+b

#tips:为mcp添加包

if __name__ == '__main__':
    fastmcp_instance.run(transport='stdio') #tips:fastmcp实例提供了run方法,
    '''
    def run(self,
        transport: Literal["stdio", "sse", "streamable-http"] = "stdio",
        mount_path: str | None = None) -> None
    '''

