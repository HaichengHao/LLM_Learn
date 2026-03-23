import time

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv('api_key')
openai_base_url = os.getenv('base_url')

openaillm = ChatOpenAI(
    model='gpt-4o-mini',
    api_key=openai_api_key,
    base_url=openai_base_url,
    temperature=1.0
)

# 定义一个通用模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个诗人"),
    ("user", "{instruction}")
])

parser = StrOutputParser()
chain = prompt | openaillm | parser

# tips:准备多个不同的指令
inputs = [
    {"instruction": "写一首七言诗赞美春天"},
    {"instruction": "写一首五言诗赞美夏天"},
    {"instruction": "写一首七言诗赞美冬天"},
]

# important:批次调用,直接使用.batch(inputs: list[Input])就可以,传入的是一个列表
#  本质上是基于多线程的!!
results = chain.batch(inputs)

start_time = time.time()
for i, res in enumerate(results, 1): #tips:第二个参数指定的是起始编号,默认是0,但是为了看着方便写成1
    print(f"=== 诗 {i} ===")
    print(res)
    print()
end_time = time.time()
total_time = end_time - start_time
print(total_time)

# tips 4.2438507080078125e-05 约4.24s,比异步批次调用慢了1.34秒