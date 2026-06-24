# @Time    : 2026/6/20 16:08
# @Author  : hero
# @File    : 19Sandboxes初识.py

'''
简单说一下它和之前backends的不同之处
它可以用文件系统的标准工具，如ls/read_file/write_file/edit_file/glob/grep
可以运行一个shell沙盒
有系统安全边界


核心思想:安全/隔离
为什么使用它？
可以让agent在沙盒中执行代码，操作文件，使用网络而不会对本地文件，安全证书和宿主机造成威胁，它是独立的
'''

from deepagents import create_deep_agent
from deepagents.backends import LangSmithSandbox
from langchain_openai import ChatOpenAI
from langsmith.sandbox import SandboxClient
from dotenv import load_dotenv
import os

load_dotenv()
langsmith_key =os.getenv('lang_smith_key')
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = f'{langsmith_key}'
client = SandboxClient()
ls_sandbox = client.create_sandbox(template_name='demo1')
backend = LangSmithSandbox(sandbox=ls_sandbox)

agent = create_deep_agent(
    model=ChatOpenAI(
        model='glm-4.7',
        api_key=os.getenv('zhipu_key'),
        base_url=os.getenv('zhipu_base_url')
    ),
    system_prompt="You are a Python coding assistant with sandbox access.",
    backend=backend,
)
try:
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Create a small Python package and run pytest",
                }
            ]
        }
    )
finally:
    client.delete_sandbox(ls_sandbox.name)