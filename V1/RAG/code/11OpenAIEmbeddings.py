# @Time    : 2026/4/2 15:26
# @Author  : hero
# @File    : 11OpenAIembedding.py
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os
load_dotenv()

api_key=os.getenv('api_key')
base_url=os.getenv('base_url')
embedd_model = OpenAIEmbeddings(
    api_key=api_key,
    base_url=base_url,
    model="text-embedding-3-small",
    dimensions=128 #tips:指定维度,不然可能默认的太大就会有点慢
)
demoquery='你好，世界'
demodocs=['你好','世界','人工智能','未来']
print(embedd_model.embed_query(demoquery))
print(embedd_model.embed_documents(demodocs))