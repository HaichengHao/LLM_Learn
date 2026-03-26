# @Time    : 2026/3/25 09:17
# @Author  : hero
# @File    : 03结合大模型调用.py
from langchain_core.prompts import PromptTemplate
from langchain_openai  import ChatOpenAI,OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser,JsonOutputParser
from langchain_core.runnables import RunnableLambda,RunnableParallel
from dotenv import load_dotenv
import os
load_dotenv()

zai_key = os.getenv('zhipu_key')
zai_base_url = os.getenv('zhipu_base_url')

model=ChatOpenAI( #tips:OpenAI()补全形式已经过时
    api_key=zai_key,
    base_url=zai_base_url,
    model='glm-4'
)


# 你叫小言,你喜欢烫头

#theway invoke,形参是字典，返回值是PromptValue

template = PromptTemplate.from_template(
    template='你叫{name},你喜欢{hobby}',
)

prompt1 = template.invoke({'name':'张三','hobby':'跑步'})
print(type(prompt1))
print(prompt1)
print(prompt1.text)
print(type(prompt1.text))
# <class 'langchain_core.prompt_values.StringPromptValue'>
# text='你叫张三,你喜欢跑步'
# 你叫张三,你喜欢跑步
# <class 'str'>

resp=model.invoke(prompt1)  #important:可以看看源码,我们可以传入PromptValue，那我们可以将prompt1传入
print(resp)
'''
content='你好！我叫张三，很高兴认识你。\n\n是的，我非常喜欢跑步。对我来说，跑步不仅仅是一项运动，更像是一种生活方式和心灵的对话。
\n\n**我为什么喜欢跑步呢？**\n\n1.  **身心放松：** 当我穿上跑鞋，迈开脚步，感觉所有的烦恼和压力都被抛在了身后。呼吸着新鲜的空气，听着风声和自己
的脚步声，大脑会变得非常清晰，这是一种绝佳的解压方式。\n2.  **挑战自我：** 我享受那种不断突破极限的感觉。无论是跑得更远，还是配速更快，每一次小小
的进步都会给我带来巨大的成就感。它让我相信自己拥有无限的潜力。\n3.  **与自然连接：** 我喜欢在公园、河边或者林间小道上跑步。四季的风景在眼前流转，
清晨的阳光和傍晚的晚霞都让我感到无比惬意。这让我感觉自己和大自然紧密地联系在一起。\n4.  **保持健康：** 跑步让我保持了健康的体魄和充沛的精力，
能以更好的状态去面对工作和生活。\n\n**我的跑步日常大概是：**\n\n*   **频率：** 每周会跑3-4次，每次5到10公里。\n*   **时间：** 比较偏爱清晨
跑，感觉一天都精神焕发。偶尔也会在夜跑，享受城市的宁静。\n*   **距离：** 目前正在备战我的第一个半程马拉松，所以训练计划会围绕这个目标展开。
\n\n你呢？你喜欢跑步吗？或者你有什么其他的运动爱好？我们可以一起交流交流！' additional_kwargs={'refusal': None} response_metadata=
{'token_usage': {'completion_tokens': 323, 'prompt_tokens': 16, 'total_tokens': 339, 'completion_tokens_details': None,
 'prompt_tokens_details': None}, 'model_provider': 'openai', 'model_name': 'glm-4', 'system_fingerprint': None,
  'id': '202603250927208aa73a3a9c89473f', 'finish_reason': 'stop', 'logprobs': None} id='lc_run--019d229a-71fb-7ab2-8471
  -7d3fafba1f9b-0' tool_calls=[] invalid_tool_calls=[] usage_metadata={'input_tokens': 16, 'output_tokens': 323, 
  'total_tokens': 339, 'input_token_details': {}, 'output_token_details': {}}
'''