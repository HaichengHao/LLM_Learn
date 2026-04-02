# @Time    : 2026/4/2 15:28
# @Author  : hero
# @File    : 12HFembedding.py
from langchain_huggingface import HuggingFaceEmbeddings
import torch
MODEL_PATH = '/home/nikofox/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/79e7739b6ab944e86d6171e44d24c997fc1e0116'
embed_local_model = HuggingFaceEmbeddings(
    model_name=MODEL_PATH,
    model_kwargs={
        'device':'cuda:0' if torch.cuda.is_available() else 'cpu'
    }
)

demo_query_local='你好'
demo_doc_local=['春眠不觉晓','gugu嘎嘎']
print(embed_local_model.embed_query(demo_query_local))
print(embed_local_model.embed_documents(demo_doc_local))