# @Time    : 2026/3/29 18:22
# @Author  : hero
# @File    : query_tst.py
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import torch

MODEL_PATH = '/home/nikofox/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/79e7739b6ab944e86d6171e44d24c997fc1e0116'

embedding_model = HuggingFaceEmbeddings(
    model_name=MODEL_PATH,
    model_kwargs={'device': 'cuda:0' if torch.cuda.is_available() else 'cpu'}
)

# 直接加载已有向量库 无需重新嵌入,
# 之前的时候是用pandas来构造一个输入和embedding数据的余弦相似度计算,而且事先自己还需要将输入进行embedding然后给数据单独开一列进行排序然后拿到top_k,
vector_db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding_model
)

# 语义搜索
results = vector_db.similarity_search("不动产物权的设立", k=2)
for i, doc in enumerate(results):
    print(f"【结果 {i+1}】\n{doc.page_content[:200]}...\n来源: {doc.metadata}\n")

'''
Loading weights: 100%|██████████| 391/391 [00:00<00:00, 42646.54it/s]
BertModel LOAD REPORT from: /home/nikofox/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/79e7739b6ab944e86d6171e44d24c997fc1e0116
Key                     | Status     |  | 
------------------------+------------+--+-
embeddings.position_ids | UNEXPECTED |  | 

Notes:
- UNEXPECTED	:can be ignored when loading from different task/architecture; not ok if you expect identical arch.
【结果 1】
第二百零七条　国家、集体、私人的物权和其他权利人的物权受法律平等保护，任何组织或者个人不得侵犯。

第二百零八条　不动产物权的设立、变更、转让和消灭，应当依照法律规定登记。动产物权的设立和转让，应当依照法律规定交付。

第二章　物权的设立、变更、转让和消灭

第一节　不动产登记

第二百零九条　不动产物权的设立、变更、转让和消灭，经依法登记，发生效力；未经登记，不发生效力，但是法律另有规定的除外。...
来源: {'source': '../../assets/sample.docx', 'start_index': 18707}

【结果 2】
第二百三十条　因继承取得物权的，自继承开始时发生效力。

第二百三十一条　因合法建造、拆除房屋等事实行为设立或者消灭物权的，自事实行为成就时发生效力。

第二百三十二条　处分依照本节规定享有的不动产物权，依照法律规定需要办理登记的，未经登记，不发生物权效力。

第三章　物权的保护

第二百三十三条　物权受到侵害的，权利人可以通过和解、调解、仲裁、诉讼等途径解决。

第二百三十四条　因物权的归属、内...
来源: {'source': '../../assets/sample.docx', 'start_index': 20473}
'''