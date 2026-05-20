# @Time    : 2026/5/18 23:51
# @Author  : hero
# @File    : 10backend之StoreBackend.py

from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.types import Command
from langchain.chat_models import init_chat_model
from deepagents.backends import StoreBackend
from dotenv import load_dotenv
import os

load_dotenv()

#StoreBackend 用于生产环境，跨Agent共享数据,持久化记忆(Redis/Postgres)




llm = init_chat_model(
    model='glm-4',
    model_provider='openai',
    api_key=os.getenv('zhipu_key'),
    base_url=os.getenv('zhipu_base_url')
)
#准备Store(模拟数据库)
## InMemoryStore是轻量级内存存储，重启后数据丢失
#最终存储的位置 内存的k=v 使用langgraph自带的,也可以换成其它的
store=InMemoryStore() #tips:也可以不用内存存储,换成数据库也是可以的,可以回看langgraph高级特性中的02中的05

#创建main_agent
main_agent=create_deep_agent(
    model=llm,
    tools=[],
    store=store,#tips:注意这里
    backend=StoreBackend, #tips:开启k=v库存储 important:触发store的前提是backend要指定为StoreBackend
    system_prompt="你要把用户的重要信息保存到user_profile.txt文件中!!"
)

#演示跨会话，跨线程进行长期记忆
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

#第一次执行,存储一些信息
result_a = main_agent.invoke(
    {
        "messages":[
            {
                "role":"user",
                "content":"今年小明19岁，已经有三年开发经验"
            }
        ]
    },
    config=config_a
)

print(f"第一次执行结果{result_a['messages'][-1].content}")

#important:读取store中的内容，看看是不是真的存进去了
items = store.search(('filesystem',)) #默认创建的命名空间名字就是filesystem,要求传入一个元组,如果是用数据库的话,这个含义其实就是数据库名称
for item in items:
    print(f'k={item.key},v={item.value}')

#第二次执行，读取一些信息

result_b = main_agent.invoke(
    {
        "messages":[
            {
                "role":"user",
                "content":"小明几岁了?有几年开发经验?"
            }
        ]
    },
    config=config_b
)
print(f"第二次返回结果{result_b['messages'][-1].content}")
'''
第一次执行结果
信息已成功保存到user_profile.txt文件中。
k=/user_profile.txt,v={'content': '用户信息：\n今年小明19岁，已经有三年开发经验', 'encoding': 'utf-8', 'created_at': '2026-05-19T02:31:17.416227+00:00', 'modified_at': '2026-05-19T02:31:17.416227+00:00'}
第二次返回结果
根据user_profile.txt文件中的信息，小明今年19岁，已经有三年开发经验。
'''