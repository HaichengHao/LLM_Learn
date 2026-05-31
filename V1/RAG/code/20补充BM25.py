#tips:uv pip install langchain-community rank_bm25

from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# 准备文档
documents = [
    Document(page_content="华为云ModelArts是面向AI开发者的平台。"),
    Document(page_content="昇思MindSpore是一个全场景AI框架。"),
    Document(page_content="ModelArts Pro是企业级AI应用开发套件。")
]

# 构建检索器
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 2

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# 混合检索
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5]
)

results = ensemble_retriever.invoke("华为的AI平台是什么")
for doc in results:
    print(doc.page_content)