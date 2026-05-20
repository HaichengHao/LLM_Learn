# @Time    : 2026/5/19 11:50
# @Author  : hero
# @File    : 12升级_上数据库.py

from deepagents.backends import StoreBackend, FilesystemBackend, CompositeBackend
from langgraph.store.postgres import PostgresStore
from langgraph.store.sqlite import SqliteStore
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from pathlib import Path
import sqlite3
import os

load_dotenv()
# store = InMemoryStore()

# db_conn = SqliteStore.from_conn_string(
#     'sqlite:///agent_workspace.db',
# )
store = SqliteStore.from_conn_string(
    'sqlite:///agent_workspace.db', )

llm = init_chat_model(
    model='glm-4',
    model_provider='openai',
    api_key=os.getenv('zhipu_key'),
    base_url=os.getenv('zhipu_base_url')
)


def create_composite_backend(runtime):
    workspace_dir = Path('./agent_workspace').resolve()
    os.makedirs(workspace_dir, exist_ok=True)

    fs_backend = FilesystemBackend(root_dir=workspace_dir, virtual_mode=True)

    store_backend = StoreBackend(store=store) #tips:这里指定StoreBackend,这样的话就实现了两种方式!!!
    return CompositeBackend(
        default=fs_backend,#tips:默认走文件系统保存【只要没有触发存储路径】
        routes={
            '/store/': store_backend #tips：如果明确指定了保存到/store/那就保存到StoreBackend,保存到内存记忆当中
        }
    )


main_agent=create_deep_agent(
    model=llm,
    store=store, #组合中也有storeBackend
    backend=create_composite_backend,
    system_prompt="""你是一个智能助手。
    - 普通文件：直接写入文件名（如 `report.txt`），保存到本地 workspace。
    - 重要记忆：写入 `/store/` 目录（如 `/store/profile.txt`），保存到store指定的存储方式中。
    """
)



#运行agent
print('测试混合存储')
config={
    "configurable":{
        "thread_id":"thread_composite"
    }
}


# 任务：同时触发两种存储路径
user_input = "1. 创建本地文件 local.txt，内容'本地文件'。\n2. 创建记忆文件 /store/memory.txt，内容'重要记忆'。"
print(f"用户指令: {user_input}")

result = main_agent.invoke({
    "messages": [{"role": "user", "content": user_input}]
}, config=config)

print("Agent 回复:", result["messages"][-1].content)

# 5. 验证结果
print("\n=== 验证本地文件 (Filesystem) ===")
# 替换 os.path.join + os.path.exists 为 Path 写法
local_path = Path("agent_workspace") / "local.txt"  # Path 拼接路径
if local_path.exists():  # Path 内置 exists 方法
    print(f"本地文件存在: {local_path}")
else:
    print("本地文件缺失")

print("\n=== 验证数据库存储 (Store) ===")
# CompositeBackend 会自动剥离路由前缀，所以 /store/memory.txt 在 Store 中的 Key 为 /memory.txt
items = store.search(("filesystem",))
for item in items:
    print(f'k={item.key},v={item.value}')


'''
测试混合存储
用户指令: 1. 创建本地文件 local.txt，内容'本地文件'。
2. 创建记忆文件 /store/memory.txt，内容'重要记忆'。
Agent 回复: 
已完成两个文件的创建：

1. `/local.txt` - 文件已存在，内容为"本地文件"
2. `/store/memory.txt` - 已创建并写入内容"重要记忆"

=== 验证本地文件 (Filesystem) ===
本地文件存在: agent_workspace/local.txt

=== 验证数据库存储 (Store) ===
k=/memory.txt,v={'content': '重要记忆', 'encoding': 'utf-8', 'created_at': '2026-05-19T03:45:37.195706+00:00', 'modified_at': '2026-05-19T03:45:37.195706+00:00'}

Process finished with exit code 0
'''