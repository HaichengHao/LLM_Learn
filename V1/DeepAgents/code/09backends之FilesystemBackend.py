# @Time    : 2026/5/18 14:54
# @Author  : hero
# @File    : 09backends之FilesystemBackend.py
from pathlib import Path
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend,StateBackend,StoreBackend,CompositeBackend
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from loguru import logger
import os
load_dotenv()


#StateBackend(默认)存在内存当中,适用于临时文件、中间计算结果，会话结束即销毁
#FilesystemBackend 存在文件系统当中

#准备本地工作目录
work_dir = Path('./agent_workspace').resolve() #resolve()等价于os.path.abspath() 取绝对路径
os.makedirs(work_dir, exist_ok=True)

#演示使用fileSystemBackEnd实现长期记忆(跨会话 跨线程)实现数据共享->多轮会话 有之前的环境
file_backend = FilesystemBackend(root_dir=work_dir,virtual_mode=True) #tips:这样就会产生一个BackendProtocol,之后的StoreBackend也是如此


llm = init_chat_model(
    model='glm-4',
    model_provider='openai',
    api_key=os.getenv('zhipu_key'),
    base_url=os.getenv('zhipu_base_url')
)

#3.创建deepagent,指定长期记忆
main_agent=create_deep_agent(
    model=llm,
    tools=[],
    backend=file_backend, #tips:要求传入的是一个BackendProtocol
    system_prompt="你是一个智能助手,可以使用文件工具进行文件操作和读写,但是只能在用户明确要求的情况下，你才可以创建文件!!!"
)

#运行并验证
print("1：：：不明确,看看会不会创建")
result_1=main_agent.invoke(
    {
        'messages':[
            {
                'role':'user',
                'content':"帮我介绍一下python语言的诞生历史"
            }
        ]
    }
)

print(result_1['messages'][-1].content)

print("2：：：明确,看看会不会创建")
result_2=main_agent.invoke(
    {
        'messages':[
            {
                'role':'user',
                'content':"帮我简短介绍一下python语言的诞生历史并且将其写入到'the_birth_of_python.txt'中"
            }
        ]
    }
)

print(result_2['messages'][-1].content)
logger.success('写入完成')



