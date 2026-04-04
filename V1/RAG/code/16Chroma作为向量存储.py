# @Time    : 2026/4/2 20:36
# @Author  : hero
# @File    : 16Chroma作为向量存储.py

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
import os
load_dotenv()

embeddings=DashScopeEmbeddings(
    model='text-embedding-v4',
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
)
texts=[
    '小世界现象（“small world” phenomenon），又称六度空间理论或六度分隔理论，是由美国心理学家斯坦利·米尔格兰姆提出的社交网络理论，认为任意两个陌生人之间建立联系所需中间人不超过六个',
    "歌曲创作:周杰倫, 派偉俊Six degrees my babyThe world is oh so vastCan you stay while they passSix degrees my babyIf separation lastsTake one step don't look back",
    'AI发展会弱化人的存在价值',
    '929年，匈牙利作家Frigyes Karinthy在短篇故事《Chains》中提出了“六度分隔理论”，他指出地球上任意两人都可以通过六层以内的熟人关系建立起联系。1967年，Stanley Milgram 进行了一系列关于社会距离的著名实验，表明在有限的1000个人的样本中，绝大多数人是通过少数熟人联系在一起的，发现了“弱纽带”关系对于维系社交网络的显著作用。后来，Duncan Watts通过追踪13个国家的24163条电子邮件关联关系，重现了Stanley Milgram的结果，并证实该网络中的平均最短距离约为6。此外，在众多社交网络中开展的全球性实验也都证实了六度分隔现象普遍存在。'
]
documents=[Document(page_content=text,metadata={'source':'manual'}) for text in texts]

vector_store=Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory='../demo.db'
)

retriver = vector_store.as_retriever(search_kwargs={'k':2})
results = retriver.invoke('什么是六度分隔')
for res in results:
    print(f'匹配到的内容\n{res.page_content[:100]}...\n来源于{res.metadata}')

