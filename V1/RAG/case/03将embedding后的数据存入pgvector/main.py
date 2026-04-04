# @Time    : 2026/4/4 14:02
# @Author  : hero
# @File    : main.py
import os
import torch
from dotenv import load_dotenv
from langchain_postgres import PGVector
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
MODEL_PATH = '/home/nikofox/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/79e7739b6ab944e86d6171e44d24c997fc1e0116'
load_dotenv()
'''
还是四个步骤

1.doc=loader.load()
2.spliter.split(doc)
3.创建embeddings
4.save2pgvector
'''


def docload(doc_path:str):
    return UnstructuredWordDocumentLoader(
        file_path=doc_path,
        mode='single'
    ).load()

def spliter(udoc,chunk_size:int=300,chunk_overlap:int=30):
    return RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', '。', '！', '？', '……', '，', ''],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True
    ).split_documents(udoc)

def embeddings(model_path:str=MODEL_PATH):
    return HuggingFaceEmbeddings(
        model_name=model_path,
        model_kwargs={
            'device':'cuda:0' if torch.cuda.is_available() else 'cpu'
        }

    )
def save2pgvector(splited_doc,embed_model):
    return PGVector.from_documents(
        documents=splited_doc,
        embedding=embed_model,
        connection=os.getenv('psql_url'),
        collection_name='demo_pgv1'
    )

if __name__ == '__main__':
    mydoc='../../assets/sample.docx'
    loaded_doc=docload(mydoc)
    splitted_doc=spliter(loaded_doc)
    embedding_model=embeddings()
    save2pgvector(splitted_doc,embedding_model)
    print('存入数据库成功')

'''
/home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/V1/RAG/case/03将embedding后的数据存入pgvector/main.py 
Loading weights: 100%|██████████| 391/391 [00:00<00:00, 68374.94it/s]
BertModel LOAD REPORT from: /home/nikofox/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/79e7739b6ab944e86d6171e44d24c997fc1e0116
Key                     | Status     |  | 
------------------------+------------+--+-
embeddings.position_ids | UNEXPECTED |  | 

Notes:
- UNEXPECTED	:can be ignored when loading from different task/architecture; not ok if you expect identical arch.
存入数据库成功
'''