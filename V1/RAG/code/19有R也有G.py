# @Time    : 2026/4/4 12:09
# @Author  : hero
# @File    : 19有R也有A.py

'''
uv add redisvl redis,对版本要求有点严格,建议5.3
'''

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_community.vectorstores import Redis
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
import os
from langchain_openai import ChatOpenAI

load_dotenv()
api_key=os.getenv('api_key')
base_url=os.getenv('base_url')
llm=ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='gpt-4o-mini'
)


embeddings=DashScopeEmbeddings(
    model='text-embedding-v4',
    dashscope_api_key=os.getenv('DASHSCOPE_API_KEY')
)

texts=[
    '小世界现象（“small world” phenomenon），又称六度空间理论或六度分隔理论，是由美国心理学家斯坦利·米尔格兰姆提出的社交网络理论，认为任意两个陌生人之间建立联系所需中间人不超过六个',
    "歌曲创作:周杰倫, 派偉俊Six degrees my babyThe world is oh so vastCan you stay while they passSix degrees my babyIf separation lastsTake one step don't look back",
    'AI发展会弱化人的存在价值',
    '929年，匈牙利作家Frigyes Karinthy在短篇故事《Chains》中提出了“六度分隔理论”，他指出地球上任意两人都可以通过六层以内的熟人关系建立起联系。1967年，Stanley Milgram 进行了一系列关于社会距离的著名实验，表明在有限的1000个人的样本中，绝大多数人是通过少数熟人联系在一起的，发现了“弱纽带”关系对于维系社交网络的显著作用。后来，Duncan Watts通过追踪13个国家的24163条电子邮件关联关系，重现了Stanley Milgram的结果，并证实该网络中的平均最短距离约为6。此外，在众多社交网络中开展的全球性实验也都证实了六度分隔现象普遍存在。'
]
documents=[Document(page_content=text,metadata={'source':'manual'}) for text in texts]
vector_store=Redis.from_documents(
    documents=documents,
    embedding=embeddings,
    redis_url='redis://127.0.0.1:65522/0', #important：注意,由于redis对于langchain的vdb有一些限制,所以只能用0号数据库
    index_name='my_index111'
)


#tips:后续可选，直接用于检索

retriever = vector_store.as_retriever(search_kwagrs={'k':2}) #tips: k为2就是top_k=2即找到最匹配的前两条
# 1. 定义 prompt
prompt = ChatPromptTemplate.from_template(
    """你是一个知识助手，请根据以下上下文回答问题：

上下文：
{context}

问题：{question}
"""
)

# 2. 构建 chain
rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
)

# 3. 调用
response = rag_chain.invoke("什么是六度分隔？")
print(response)