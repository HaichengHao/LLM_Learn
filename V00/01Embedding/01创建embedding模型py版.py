# @Time    : 2026/3/15 15:32
# @Author  : hero
# @File    : 01创建embedding模型py版.py

import pandas as pd
import os
from openai import OpenAI
import tiktoken
from dotenv import load_dotenv
load_dotenv()

#指定vpn的地址和端口


#tips:数据集来自amazon美食数据,其中包括最近1000条评论,英文


#step 1:读取数据

df = pd.read_csv('./datas/fine_food_reviews_1k.csv')

df   = df[df.columns[1:]]
df=df.dropna()
df['combined']="Title:"+df.Summary.str.strip()+"; Content"+df.Text.str.strip()
embedding_model="text-embedding-ada-002"
tokenizer_name= 'cl100k_base' #tips:指定分词器
max_tokens=8191
top_n=1000
df = df.sort_values('Time')
df.drop('Time',axis=1,inplace=True)
tokenizer=tiktoken.get_encoding(encoding_name=tokenizer_name)
df['count_token']=df.combined.apply(lambda x: len(tokenizer.encode(x)))
df = df[df.count_token  <= max_tokens].tail(top_n)

client = OpenAI()
def embedding_text(text,model="text-embedding-ada-002"):
    resp = client.embeddings.create(input=text,model=model)
    return resp.data[0].embedding

df['embedding']=df.combined.apply(embedding_text)