# @Time    : 2026/6/3 12:01
# @Author  : hero
# @File    : 16补充redisstore.py

'''
首先安装好包
(LLMlearn) nikofox@MOSS:~/LLMlearn/V1/gradio$ uv add langgraph-checkpoint-redis redis
Resolved 358 packages in 6.69s
Prepared 1 package in 716ms
Installed 1 package in 4ms
 + langgraph-checkpoint-redis==0.4.1

 并且第一次使用需要调用 store.setup() 创建索引。

本地启动 Redis，建议直接用 Redis Stack 或 Redis 8+。因为 LangGraph Redis Store 依赖 RedisJSON 和 RediSearch；Redis 8+ 默认包含这些模块，Redis 8 以下建议用 Redis Stack。
'''

from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.store.redis import RedisStore #tips:使用redisstore
from langgraph.types import Command
from langchain.chat_models import init_chat_model
from deepagents.backends import StoreBackend
from dotenv import load_dotenv
import os

load_dotenv()

#StoreBackend 用于生产环境，跨Agent共享数据,持久化记忆(Redis/Postgres)




llm = init_chat_model(
    model='glm-4.7',
    model_provider='openai',
    api_key=os.getenv('zhipu_key'),
    base_url=os.getenv('zhipu_base_url')
)
#准备Store(模拟数据库)
## InMemoryStore是轻量级内存存储，重启后数据丢失
#最终存储的位置 内存的k=v 使用langgraph自带的,也可以换成其它的
store=InMemoryStore() #tips:也可以不用内存存储,换成数据库也是可以的,可以回看langgraph高级特性中的02中的05


#important:设置redisstore ,它智能用0号库
REDIS_URI=os.getenv('REDIS_DOCKER0')

with RedisStore.from_conn_string(REDIS_URI) as redis_store:
    redis_store.setup()  #important:注意,首次最好是setup一次

    #创建main_agent
    main_agent=create_deep_agent(
        model=llm,
        tools=[],
        store=redis_store,#tips:注意这里
        backend=StoreBackend(), #tips:开启k=v库存储 important:触发store的前提是backend要指定为StoreBackend,新版本建议直接传实例StoreBackend()
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
    # 这里要查redis_store而不是原来的InMemoryStore
    items = redis_store.search('filesystem',) #tips: StoreBackend 默认把文件系统内容放在 ("filesystem",) 这个 namespace 下
                                              #  namespace 是 LangGraph Store 的逻辑命名空间，不等于数据库名称
    for item in items:
        print(f'k={item.key},v={item.value}')

    #tips：第二次执行,换thread_id,但仍然能读取到长期store

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
    /home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/V1/DeepAgents/code/16补充redisstore.py 
    第一次执行结果已将小明的信息保存到 user_profile.txt 文件中。
    第二次返回结果小明19岁，有3年开发经验。
    '''

#tips:redis数据库中的结果可以查看note下的01.png