# @Time    : 2026/6/3 14:08
# @Author  : hero
# @File    : 17redisstore与redissaver配合.py


'''
如果你后面还想把 对话线程状态 也放到 Redis，而不只是长期文件 Store，那么再加 RedisSaver
'''
from deepagents import create_deep_agent
from deepagents.backends import StoreBackend
from langchain.chat_models import init_chat_model
from langgraph.store.redis import RedisStore
from langgraph.checkpoint.redis import RedisSaver #tips:引入redissaver
from dotenv import load_dotenv
import os

load_dotenv()

llm = init_chat_model(
    model="glm-4.7",
    model_provider="openai",
    api_key=os.getenv("zhipu_key"),
    base_url=os.getenv("zhipu_base_url"),
)

REDIS_URI = os.getenv("REDIS_DOCKER0")

if not REDIS_URI:
    raise ValueError("请先在 .env 中配置 REDIS_DOCKER，例如 redis://localhost:6379")

#important:都用上下文引入
with RedisStore.from_conn_string(REDIS_URI) as redis_store, \
     RedisSaver.from_conn_string(REDIS_URI) as checkpointer:

    #tips:注意这里都要setup
    redis_store.setup()
    checkpointer.setup()

    main_agent = create_deep_agent(
        model=llm,
        tools=[],
        store=redis_store,              # 长期记忆，例如 user_profile.txt
        checkpointer=checkpointer,      # 短期线程状态，例如 thread_id 对话历史
        backend=StoreBackend(),
        system_prompt="你要把用户的重要信息保存到/memories/user_profile.txt文件中!!",
    )

    config_a = {
        "configurable": {
            "thread_id": "demo1"
        }
    }

    result = main_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "今年小红21岁，已经有三年开发经验"
                }
            ]
        },
        config=config_a,
    )

    print(result["messages"][-1].content)

    items = redis_store.search(("filesystem",))

    for item in items:
        print(f"k={item.key}, v={item.value}")

'''
已保存用户信息到 /memories/user_profile.txt 文件。
k=/user_profile.txt, v={'content': '用户档案\n\n姓名：小明\n年龄：19岁\n开发经验：3年', 'encoding': 'utf-8', 'created_at': '2026-06-03T06:03:16.027503+00:00', 'modified_at': '2026-06-03T06:03:16.027503+00:00'}
k=/memories/user_profile.txt, v={'content': '用户信息：\n- 姓名：小红\n- 年龄：21岁\n- 工作经验：3年开发经验', 'encoding': 'utf-8', 'created_at': '2026-06-03T06:17:24.285188+00:00', 'modified_at': '2026-06-03T06:17:24.285188+00:00'}'''