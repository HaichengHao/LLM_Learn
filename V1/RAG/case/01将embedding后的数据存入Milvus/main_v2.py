from langchain_milvus import Milvus
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from dotenv import load_dotenv
import os
import torch
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection,utility
import numpy as np


load_dotenv()

MODEL_PATH = '/home/nikofox/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/79e7739b6ab944e86d6171e44d24c997fc1e0116'

# ❌ 不再使用 URI 文件
# URI = "./milvus_example.db"


# ✅ 1. 连接 Docker Milvus
connections.connect(
    alias="default",
    host="localhost",
    port="19530"
)


def loadded_doc(doc_pth: str):
    return UnstructuredWordDocumentLoader(
        file_path=doc_pth,
        mode='single'
    ).load()


def splited_doc(doc, chunk_size: int = 500, chunk_overlap: int = 50):
    return RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', '。', '！', '？', '……', '，', ''],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True
    ).split_documents(doc)


def embedding():
    return HuggingFaceEmbeddings(
        model_name=MODEL_PATH,
        model_kwargs={
            'device': 'cuda:0' if torch.cuda.is_available() else 'cpu',
        }
    )


# def save2milvus(documents, emb_model):
#     vector_store = Milvus(
#         embedding_function=emb_model,
#         connection_args={
#             "host": "localhost",
#             "port": "19530",
#             "alias":"default",
#         },
#         collection_name="document_collection",
#         drop_old=True
#     )
#
#     texts = [doc.page_content for doc in documents]
#     metadatas = [doc.metadata for doc in documents]
#
#     vector_store.add_texts(texts=texts, metadatas=metadatas)
#
#     return vector_store
def save2milvus(documents, emb_model):
    # 1️⃣ 连接
    connections.connect(host="localhost", port="19530")
    # ❗删除旧表（关键）
    if utility.has_collection("document_collection"):
        utility.drop_collection("document_collection")
    # 2️⃣ 定义 schema
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
    ]

    schema = CollectionSchema(fields, description="document collection")

    # 3️⃣ 创建 collection
    collection = Collection("document_collection", schema)

    # 4️⃣ embedding
    texts = [doc.page_content for doc in documents]
    embeddings = emb_model.embed_documents(texts)

    # 5️⃣ 插入数据
    data = [
        embeddings,
        texts
    ]

    collection.insert(data)
    collection.create_index(
        field_name="embedding",
        index_params={
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
    )

    collection.load()
    return collection

if __name__ == '__main__':
    mdoc = '../../assets/sample.docx'
    loadded_mdoc = loadded_doc(mdoc)
    splited_mdoc = splited_doc(loadded_mdoc)
    embedding_model = embedding()

    vector_store = save2milvus(splited_mdoc, embedding_model)

    print('✅ 数据成功存入 Milvus (Docker版)')