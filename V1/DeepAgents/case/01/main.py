# @Time    : 2026/6/10 22:26
# @Author  : hero
# @File    : main.py

from langchain.agents.middleware import SummarizationMiddleware,ModelCallLimitMiddleware,ToolCallLimitMiddleware
from langgraph.store.redis import RedisStore
from langgraph.checkpoint.redis import RedisSaver
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend,StoreBackend,CompositeBackend
from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv()
REDIS_URI=os.getenv('REDIS_DOCKER0')
llm=init_chat_model(
    model='glm-4.7',
    model_provider='openai',
    api_key=os.getenv('zhipu_key'),
    base_url=os.getenv('zhipu_base_url')
)


#step 1 创建fileSystemBackend通过设置skill技能所在的文件夹
current_dir=Path(__file__).parent.resolve()
print(current_dir)

# file_backend=FilesystemBackend(
#     root_dir=current_dir,
#     virtual_mode=True
# )


def create_composite_backend(runtime):
    """
    CompositeBackend 路由规则：

    1. 默认路径：
       使用 StoreBackend()
       也就是写入 LangGraph Store，这里对应 RedisStore。

    2. /fs_store/ 开头的路径：
       使用 FilesystemBackend()
       也就是写入本地 workspace 目录。
    """
    workspace_dir = current_dir / 'workspace'
    os.makedirs(workspace_dir, exist_ok=True)
    fs_backend = FilesystemBackend(
        root_dir=workspace_dir,
        virtual_mode=True
    )

    return CompositeBackend(
        default=StoreBackend(), #tips:默认是Storebackend
        routes={
            '/fs_store/':fs_backend
        }
    )

#step 2 建立deepagent并设置skill所在的文件夹(相对于file_backlend的目录下)
with RedisStore.from_conn_string(REDIS_URI) as redis_store:
    with RedisSaver.from_conn_string(REDIS_URI) as checkpointer:
        redis_store.setup()   #设置一下setup,加上更稳
        checkpointer.setup()
        main_agent=create_deep_agent(
            model=llm,
            tools=[],
            system_prompt="""
            你是一名智能助手。

            存储规则：
            - 对话历史：由 LangGraph checkpointer 自动保存到 Redis。
            - 长期记忆：如果用户要求保存重要信息，可以写入普通文件名，例如 user_profile.txt。
            - 本地文件：如果用户要求保存到本地 workspace，请使用 /fs_store/ 路径。
            - 例如 /fs_store/a.txt 会保存到本地 workspace。
            - 例如 user_profile.txt 会保存到 Redis Store。
            """,
            # skills=[
            #     "skills"
            # ],
            store=redis_store,
            backend=create_composite_backend,
            checkpointer=checkpointer
        )


        config={
            "configurable":{
                "thread_id":"demo1"
            }
        }

        query1 = "帮我用一段精简的话讲解一下 RTX2080Ti 的诞生历史，写入到 /fs_store/the_history_of_cuda.txt"

        result = main_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": query1
                    }
                ]
            },
            config=config
        )

        print("第一轮结果：")
        print(result["messages"][-1].content)

        query2 = "我刚才让你写入的文件名是什么？"

        result2 = main_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": query2
                    }
                ]
            },
            config=config
        )

        print("第二轮结果：")
        print(result2["messages"][-1].content)

        print("Redis Store filesystem namespace 内容：")
        items = redis_store.search(("filesystem",))
        for item in items:
            print(f"k={item.key}, v={item.value}")

'''
/home/nikofox/LLMlearn/V1/DeepAgents/case/01
第一轮结果：
已完成。已将RTX2080Ti的诞生历史写入 /fs_store/the_history_of_cuda.txt。
第二轮结果：
/fs_store/the_history_of_cuda.txt
Redis Store filesystem namespace 内容：'''