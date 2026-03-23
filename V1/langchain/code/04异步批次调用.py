# @Time    : 2026/3/23 14:12
# @Author  : hero
# @File    : 04异步批次调用.py
import time

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

openai_api_key = os.getenv('api_key')
openai_base_url = os.getenv('base_url')

# 定义大模型
openaillm = ChatOpenAI(
    model='gpt-4o-mini',
    api_key=openai_api_key,
    base_url=openai_base_url,
    temperature=1.0
)

# ✅ 修正模板：使用 {instruction} 作为变量占位符
prompt = ChatPromptTemplate.from_messages([
    ("system", "你现在是一个超级伟大的诗人"),
    ("user", "{instruction}")  # ← 这里是关键！
])

parser = StrOutputParser()
chain = prompt | openaillm | parser

# 输入数据
inputs = [
    {"instruction": "写一首七言诗赞美春天"},
    {"instruction": "写一首五言诗赞美夏天"},
    {"instruction": "写一首七言诗赞美冬天"},
]

# ❌ 错误：ainvoke 不能用于批量
# res2 = chain.ainvoke(input=inputs)

# ✅ 正确：使用 abatch 进行异步批量调用
async def run_async_batch():
    results = await chain.abatch(inputs) #important:abatch期待的输入是一个列表输入，查看其源码发现其返回值是一个List[Output],返回的是一个列表

    #tips:然后我们可以迭代拿出来结果
    for i, res in enumerate(results, 1):
        print(f"=== 诗 {i} ===")
        print(res)
        print()

# 运行异步函数
if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(run_async_batch())
    end_time = time.time()

    total_time = end_time - start_time
    print(total_time)

"""
=== 诗 1 ===
春风拂面花竞开，
绿柳轻摇入画来。
燕语呢喃铺暖意，
细雨润心润土栽。
桃红灿烂映晴空，
蜂舞蝶飞自在徘。
好景无限催人醉，
人间四月春光回。

=== 诗 2 ===
夏日炎炎艳阳高，  
绿荫如盖醉人豪。  
清风徐来送凉意，  
花开遍地竞芳华。  
悠然闲适好时光。  

=== 诗 3 ===
白雪纷飞覆大地，  
银妆素裹似仙境。  
寒风呼啸铸冰霜，  
晶莹玉树挂银铃。  

炉边温酒话暖春，  
腊梅傲雪香盈盈。  
冬日虽冷情却暖，  
愿随岁月共长吟。  


2.904594898223877  约2.9秒,确实比单纯的非异步批次调用快
"""