# @Time    : 2026/4/3 17:21
# @Author  : hero
# @File    : main.py

from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_openai import OpenAIEmbeddings
from langchain_redis import RedisConfig,RedisVectorStore#tips:这次尝试一个新的,
from langchain_community.vectorstores import Redis #tips:之前用的是这个
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os

from pymilvus import connections

load_dotenv()

api_key = os.getenv("api_key")
base_url = os.getenv("base_url")

'''
依然四步走
1.读取文件并用loader.load()
2.将加载的文件用spliter.split(doc)
3.将分割后的文件进行embedding
4.将其存入redis-stack-server
'''

def load_doc(doc_path:str):
    return UnstructuredWordDocumentLoader(
        file_path=doc_path,
        mode='single'
    ).load()

def split_doc(doc,chunk_size=400,chunk_overlap=50):
    return RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', '。', '！', '？', '……', '，', ''],  # tips:分割符列表,按顺序切分，现用句号切分，然后是感叹号，然后问号,然后省略号，然后逗号，然后空
        chunk_size=chunk_size,  # 每个块儿的最大长度
        chunk_overlap=chunk_overlap,  # tips:每个块重叠的长度
        length_function=len,  # tips:可选,计算文本长度的函数，默认为字符串长度,可以自定义函数来实现token数切分
        add_start_index=True  # tips:可选,块的元数据中添加如此块起始索引

    ).split_documents(doc)

def embeddings():
    return OpenAIEmbeddings(
        api_key=api_key,
        base_url=base_url,
        model="text-embedding-3-small"
    )

def save2redis(udocuments,embedding_model):
    RedisVectorStore.from_documents(
        documents=udocuments,
        embedding=embedding_model,
        config=RedisConfig(
            index_name='demo_index',
            redis_url='redis://127.0.0.1:65522/0'
        )
    )

if __name__ == '__main__':
    mydoc_path='../../assets/sample.docx'
    loaded_doc=load_doc(mydoc_path)
    splited_doc=split_doc(loaded_doc)
    u_embedding_model=embeddings()
    save2redis(
        splited_doc,
        u_embedding_model
    )
    print('成功存入redis-stack-server🎉')