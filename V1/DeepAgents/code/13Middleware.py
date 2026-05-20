# @Time    : 2026/5/19 15:03
# @Author  : hero
# @File    : 13Middleware.py
from deepagents.backends import StoreBackend, FilesystemBackend, CompositeBackend
from langgraph.store.memory import InMemoryStore
from langchain_core.tools import tool
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import SummarizationMiddleware,ModelCallLimitMiddleware,ToolCallLimitMiddleware
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()
store = InMemoryStore()

llm = init_chat_model(
    model='glm-4',
    model_provider='openai',
    api_key=os.getenv('zhipu_key'),
    base_url=os.getenv('zhipu_base_url')
)



@tool
def del_table(table_name: str):
    """
    高危动作工具,删除传入的表
    :param table_name:
    :return:
    """
    # 伪代码
    print(f'【调用了删除表的工具】>>>删除了{table_name}表')

    return f'删除了表{table_name}'


# 删除文件工具

@tool
def del_file(file_name: str):
    """
    删除文件
    :param file_name:
    :return:
    """
    print(f'【调用了删除文件的工具】>>>删除了{file_name}文件')

    return f'删除了文件{file_name}'


# 查询表数据工具

@tool
def select_database(table_name: str):
    """
    查询表数据
    :param table_name:
    :return:
    """
    print(f'【调用了查询数据的工具】>>>查询了{table_name}表!!')
    return f'查询了{table_name}的数据'

check_pointer = InMemorySaver()

agent = create_deep_agent(
    model=llm,
    tools=[del_table, del_file, select_database],
    system_prompt="回答使用中文,调用对应的工具实现对应的功能!",
    interrupt_on={
        "del_table": False,  # 通过/编辑/拒绝
        "del_file": False,  # 通过/编辑/拒绝
        "select_database": False,  # 这里意思就是你查数据不用请求我的同意
        # tips:或者还有这种写法: 'delete_file":["approve","reject","edit"] 这样用列表指定自己想用的操作
    },
    middleware={
        SummarizationMiddleware(
            model=llm, #tips:指定总结上下文要用的模型
            trigger=('tokens',4000), #tips:配置触发总结上下文的条件 这里配置的是达到4000tokens时触发(一般情况下是模型的2/3)
            keep=('messages',20) #tips:指定在最近的20个messages中获取信息
        ),
        ModelCallLimitMiddleware( #tips:设置模型调用限制中间件
            thread_limit=10, #一次执行线程内调用模型的次数->也就是同一个thread_id下调用模型的次数,一般情况下,thread_limit和run_limit是一样的
            run_limit=5, #一次会话内调用模型的次数
            #上面二者可以这样理解,thread_limit表示你可以开十个会话窗口,run_limit表示每个窗口你可以有5次问问题的机会

            exit_behavior="end" #达到限制之后，就结束，还可以设置成error，达到限制之后就报错
        ),
        ToolCallLimitMiddleware(
            tool_name="del_table",
            thread_limit=10,
            run_limit=5,

        ),
    },
    checkpointer=check_pointer
)

config={
    'configurable':{
        'thread_id':'user_ 1'
    }
}
result = agent.invoke(
{
        "messages": [
            {
                'role': 'user',
                'content': '查询一下product表的数据;再删除user表,最后删除haha.txt文件'
            }
        ]
    },
    config=config
)