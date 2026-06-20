# @Time    : 2026/6/20 13:11
# @Author  : hero
# @File    : 21补充之增量更新.py
import torch
import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
MODEL_PATH = '/home/nikofox/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/79e7739b6ab944e86d6171e44d24c997fc1e0116'


#初始化(加载已有库)
client = chromadb.PersistentClient(
    path='demo_milvus.db'
)

embeddings = HuggingFaceEmbeddings(
    model_name=MODEL_PATH,
    model_kwargs={
        'device': 'cuda:0' if torch.cuda.is_available() else 'cpu'
    }
)

vector_store=Chroma.from_documents(
    client=client,
    collection_name='vectors',
    embeddings=embeddings,
)


# 新增文档（自动计算 embedding 并追加）
new_docs = [ ... ]  # 新的 Document 对象列表
vector_store.add_documents(new_docs)  # ← 关键：直接 append！