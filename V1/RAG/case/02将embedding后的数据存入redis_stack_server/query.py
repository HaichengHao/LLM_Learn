# @Time    : 2026/4/3 17:58
# @Author  : hero
# @File    : query.py
from langchain_openai import OpenAIEmbeddings
from langchain_redis import RedisConfig,RedisVectorStore
from dotenv import load_dotenv
import os
load_dotenv()
api_key=os.getenv('api_key')
base_url=os.getenv('base_url')

embeddings=OpenAIEmbeddings(
    api_key=api_key,
    base_url=base_url,
    model='text-embedding-3-small'
)
vector_store=RedisVectorStore(
    embeddings=embeddings,
    config=RedisConfig(
        redis_url='redis://127.0.0.1:65522/0',
        index_name='demo_index',
    )

)

#tips:利用向量数据库进行语义搜索
results=vector_store.similarity_search('国家、集体、私人的物权和其他权利人的物权受法律平等保护',k=3)
for i,doc in enumerate(results,start=1):
    print(f'结果{i},\n{doc.page_content[:60]}...\n\t\t来源{doc.metadata}\n')

'''
结果1,
第五章　民事权利

第一百零九条　自然人的人身自由、人格尊严受法律保护。

第一百一十条　自然人享有生命权、身体权、健康...
		来源{'source': '../../assets/sample.docx', 'start_index': 10833}

结果2,
第二百三十七条　造成不动产或者动产毁损的，权利人可以依法请求修理、重作、更换或者恢复原状。

第二百三十八条　侵害物权，...
		来源{'source': '../../assets/sample.docx', 'start_index': 20773}

结果3,
第二百零七条　国家、集体、私人的物权和其他权利人的物权受法律平等保护，任何组织或者个人不得侵犯。  

第二百零八条　不动产...
		来源{'source': '../../assets/sample.docx', 'start_index': 18707}


'''

#结果三是匹配到了,这次选的模型不理想,甚至不如本地的huggingface模型