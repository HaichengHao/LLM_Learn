# @Time    : 2026/3/27 17:34
# @Author  : hero
# @File    : 23Tavily搜索工具.py
'''
当我们问模型实时信息时它是不知道的,
这时候我们需要借助Tavily搜索工具让它联网搜索
'''


from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
import os
load_dotenv()
api_key=os.getenv('zhipu_key')
base_url=os.getenv('zhipu_base_url')
# tavily_key = os.getenv('tavily_key') #tips:注意要先去网站注册!!https://app.tavily.com/home,还有现在不支持这样了
'''
.env 中的变量名改为 TAVILY_API_KEY⚠️
'''
model = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='glm-5'
)


#important:langchain内置的一个工具,可以轻松地使用Tavily搜索引擎作为工具
search = TavilySearch(

    max_results=2, #tips:定义只返回两个结果,默认5个
)

res = search.invoke('今天辽宁沈阳市和平区的天气怎么样?')

print(res)
'''
/home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/V1/langchain/code/23Tavily搜索工具.py 
{'query': '今天辽宁沈阳市和平区的天气怎么样?', 'follow_up_questions': None, 'answer': None, 'images': [], 
'results': [{'url': 'https://tianqi.moji.com/weather/china/liaoning/heping-district', 
'title': '沈阳市和平区天气预报', 'content': '沈阳市和平区今天实况：17度晴，湿度：33%，西风：5级。白天：19度,晴。 夜间：晴，1度，天气偏凉了，
墨迹天气建议您穿上厚些的外套或是保暖的羊毛衫，年老体弱者可以选择保暖的摇', 'score': 0.92588276, 'raw_content': None}, 
{'url': 'http://www.zhgfn.cn/weather.php?id=452', 'title': '沈阳市和平区天气预报7天', 'content': '辽宁省气象局2026年03月22日01:10预计，
沈阳市和平区今日天气多云，7°C，湿度: 53%，风速: 3-4级，风向: 东南风，，天气预警数量：0条，查询结果偶有误差，仅供参考！', 'score': 0.8965509, 
'raw_content': None}], 'response_time': 0.77, 'request_id': '5162d4f1-16ce-4269-b124-b3524eb0ac29'}
'''
#tips:让模型绑定工具
# model.bind_tools([search])