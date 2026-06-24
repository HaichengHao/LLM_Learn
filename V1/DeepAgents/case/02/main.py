from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.redis import RedisSaver
from langgraph.store.redis import RedisStore
from dotenv import load_dotenv
from deepagents.backends import FilesystemBackend, StoreBackend, CompositeBackend
from deepagents.middleware import SummarizationMiddleware
from pathlib import Path
from loguru import logger
import os

load_dotenv()

REDIS_URL = os.getenv("REDIS_DOCKER0")
CURRENT_DIR = Path(__file__).parent.resolve()

logger.info(f"current dir is {CURRENT_DIR}")

llm = init_chat_model(
    model="glm-4.7",
    model_provider="openai",
    api_key=os.getenv("zhipu_key"),
    base_url=os.getenv("zhipu_base_url"),
)

# step =========创建混合 backend 实例=============

workspace_dir = CURRENT_DIR / "workspace"
skills_dir = CURRENT_DIR / "skills"

os.makedirs(workspace_dir, exist_ok=True)
os.makedirs(skills_dir, exist_ok=True)

# step =======做一个检查=========================
skill_file = skills_dir / "emoji-translator" / "SKILL.md"
print("skills_dir =", skills_dir)
print("skill_file exists =", skill_file.exists())
print("skill_file =", skill_file)

if skill_file.exists():
    print(skill_file.read_text(encoding="utf-8")[:300])

workspace_backend = FilesystemBackend(
    root_dir=workspace_dir,
    virtual_mode=True,
    max_file_size_mb=12,
)

skills_backend = FilesystemBackend(
    root_dir=skills_dir,
    virtual_mode=True,
    max_file_size_mb=12,
)

composite_backend = CompositeBackend(
    default=StoreBackend(
        namespace=lambda ctx: (
            "deepagents",
            "store",
            ctx.config.get("configurable", {}).get("thread_id", "default"),
        )
    ),
    routes={
        "/skills/": skills_backend,
        "/fs_store_backend/": workspace_backend,
    },
)

with RedisStore.from_conn_string(REDIS_URL) as redis_store:
    with RedisSaver.from_conn_string(REDIS_URL) as redis_saver_ckpt:
        redis_store.setup()
        redis_saver_ckpt.setup()

        dp_agent = create_deep_agent(
            model=llm,
            tools=[],
            system_prompt="""
                    你是一名智能助手。
                    你会使用 skills。
                    
                    存储规则：
                    - 对话历史：由 LangGraph checkpointer 自动保存到 Redis。
                    - 长期记忆：如果用户要求保存重要信息，可以写入普通文件名，例如 user_profile.txt。
                    - 本地文件：如果用户要求保存到本地 workspace，请使用 /fs_store_backend/ 路径。
                    - 例如 /fs_store_backend/a.txt 会保存到本地 workspace。
                    - 例如 user_profile.txt 会保存到 Redis Store。
                """,
            skills=["/skills/"],
            middleware=[
                SummarizationMiddleware(
                    model=llm,
                    trigger=('tokens',4000),
                    keep=('messages',20),
                )
            ],
            store=redis_store,
            backend=composite_backend,
            checkpointer=redis_saver_ckpt,
        )

        config = {
            "configurable": {
                "thread_id": "thread_demo1"
            }
        }

        # query_1 = "你有什么技能?"
        query_1 = "请把这句话翻译成 emoji：我今天很开心，想去喝咖啡"
        result = dp_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": query_1,
                    }
                ]
            },
            config=config,
        )

        print(result['messages'][-1].content)