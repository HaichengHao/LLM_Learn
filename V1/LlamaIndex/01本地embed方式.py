import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# 使用 LlamaIndex 原生的 OpenAILike 来对接兼容接口
from langchain_community.chat_models import ChatTongyi
from llama_index.embeddings.dashscope import DashScopeEmbeddings
# 1. 加载环境变量
load_dotenv()

# 2. 设置嵌入模型 (Embedding Model)
MODEL_PATH = '/home/nikofox/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/79e7739b6ab944e86d6171e44d24c997fc1e0116'
Settings.embed_model = HuggingFaceEmbedding(model_name=MODEL_PATH)

# 3. 设置大语言模型 (LLM) - 修正拼写并使用 OpenAILike
Settings.llm = ChatTongyi(
    name=os.getenv('QWEN_MODEL'),
    api_key=os.getenv('QWEN_KEY'),
)

# --- 原有代码 ---
documents = SimpleDirectoryReader(input_dir="./data").load_data()
index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()
response = query_engine.query("langchain是什么")
print(response)