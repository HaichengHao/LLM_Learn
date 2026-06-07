# @Time    : 2026/6/3 20:54
# @Author  : hero
# @File    : 18PostgresStorebackend.py
from langgraph.store.postgres import PostgresStore
from deepagents import create_deep_agent
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from deepagents.backends import StoreBackend
from langchain.agents.middleware import SummarizationMiddleware,ModelCallLimitMiddleware
import os

load_dotenv()

llm=init_chat_model(
    model='glm-4.7',
    model_provider='openai',
    api_key=os.getenv("zhipu_key"),
    base_url=os.getenv("zhipu_base_url")
)

@tool
def del_table(table_name:str):
    """
    高危操作工具,删除传入的表
    :param table_name: 表名
    :return:
    """
    #伪代码
    print(f'调用了删除表的工具>>>删除了{table_name}')

    return f'{table_name}表被删除'

with PostgresStore.from_conn_string(
    conn_string=os.getenv('PSQL_CONN'), #tips:PostgresStore.from_conn_string() 底层走的是 psycopg，它需要普通 PostgreSQL 连接串，不是 SQLAlchemy 连接串。
) as psql_store:
    psql_store.setup()
    main_agent=create_deep_agent(
        model=llm,
        tools=[del_table],
        store=psql_store,
        backend=StoreBackend,
        system_prompt="你要把用户的重要信息保存到user_profile.txt文件中!!"

    )

    config_a={
        "configurable":{
            "thread_id":"demo1"
        }
    }
    config_b={
        "configurable":{
            "thread_id":"demo2"
        }
    }


    #执行一次操作,存储一些信息

    result_a=main_agent.invoke(
        {
            "messages":[
                {
                    "role":"user",
                    "content":"今年小明19岁，已经有三年开发经验"
                }
            ]
        },
        config=config_a,
    )

    print(f'第一次执行结果{result_a["messages"][-1].content}')

    items=psql_store.search('filesystem')

    for item in items:
        print(f'k={item.key},v={item.value}')


    #tips:第二次执行,替换thread_id
    result_b=main_agent.invoke(
        {
            'messages':[
                {
                    'role':'user',
                    'content':'小明几岁了?有几年开发经验?'
                }
            ]
        },
        config=config_b,
    )

    print(f'第二次返回结果{result_b["messages"][-1].content}')

'''
/home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/V1/DeepAgents/code/18PostgresStorebackend.py 
第一次执行结果已将小明的重要信息保存到user_profile.txt文件中。
第二次返回结果小明19岁，有3年开发经验。

Process finished with exit code 0'''