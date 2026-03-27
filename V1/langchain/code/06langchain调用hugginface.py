# @Time    : 2026/3/23 15:10
# @Author  : hero
# @File    : 06langchain调用hugginface.py
import torch
import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import ChatHuggingFace
# 👇👇👇 关键步骤：设置国内镜像源 (必须在 import sentence_transformers 之前设置)
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
from transformers import AutoTokenizer, AutoModelForCausalLM

load_dotenv()

model_name = "Qwen/Qwen1.5-1.8B-Chat"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map='auto',
    torch_dtype=torch.float16,
    trust_remote_code=True
)

llm_local = ChatHuggingFace(
    model=model,
    tokenizer=tokenizer,
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "把下面的语句翻译成{language}"),
        ("user", "{user_text}")
    ]
)

parser = StrOutputParser()
chain = prompt | llm_local | parser

res = chain.invoke(
    {
        'language': '英文', 'user_text': '春眠不觉晓'
    }
)

print(res)
