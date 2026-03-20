# @Time    : 2026/3/20 09:17
# @Author  : hero
# @File    : demo笑话.py
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
from langchain_huggingface import HuggingFacePipeline
from transformers import pipeline
from langchain_core.prompts import PromptTemplate
import torch

print("CUDA available: ", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))

hf_pipe = pipeline(
    task="text-generation",
    model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    device=0,
    torch_dtype=torch.float16,
    trust_remote_code=False,
    max_new_tokens=128,
    do_sample=True,
    temperature=0.7
)
llm = HuggingFacePipeline(pipeline=hf_pipe)

prompt = PromptTemplate.from_template("{input}")
chain = prompt | llm

result = chain.invoke({"input": "讲一个笑话"})
print(result)
