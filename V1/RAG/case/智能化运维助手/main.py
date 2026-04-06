# @Time    : 2026/4/5 14:41
# @Author  : hero
# @File    : main.py
'''
uv add docx2txt
uv add python-docx
uv add unstructured
'''

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_redis import RedisConfig,RedisChatMessageHistory
from dotenv import load_dotenv
import os
