# @Time    : 2026/3/20 11:03
# @Author  : hero
# @File    : demo1.py
from openai  import OpenAI
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('API_KEY')
if not api_key:
    raise ValueError('你还没配key')
#tips:连第三方
client = OpenAI(
    base_url='https://xiaoai.plus/v1', #tips：如果用openai的就写openai的
    # sk-xxx替换为自己的key
    # api_key='sk-xxx'
    api_key=api_key
)

resp = client.embeddings.create(
    model="text-embedding-3-small", #tips:选择模型
    input="万物ai", #tips:定义输入
    dimensions=512 #tips:定义维度,之后输出的长度就会是512了
)

#tips:打印生成的向量
print(resp)
print(resp.data[0].embedding)
print(len(resp.data[0].embedding))

'''
CreateEmbeddingResponse(data=[Embedding(embedding=[-0.0037771800998598337, 0.005390174686908722, ..... 0.033409614115953445]
1536
'''