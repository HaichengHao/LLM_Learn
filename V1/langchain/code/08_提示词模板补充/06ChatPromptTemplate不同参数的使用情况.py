# @Time    : 2026/3/25 10:45
# @Author  : hero
# @File    : 06ChatPromptTemplate不同参数的使用情况.py
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
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


'''
def __init__(self,
             messages: Sequence[BaseMessagePromptTemplate | BaseMessage | BaseChatPromptTemplate | tuple[str | type, str | Sequence[dict] | Sequence[object]] | str | dict[str, Any]],
             *,
             template_format: Literal["f-string", "mustache", "jinja2"] = "f-string",
             **kwargs: Any) -> None
             
             '''

#tips:messages可以传入很多种类型，元组、字符串、字典、列表、消息类型、ChatPromptTemplate,BaseMessagePromptTemplate等构成的列表
prompt_template = ChatPromptTemplate(
    messages=[
        ('system','你叫{uname}'),
        ('human','你好，我的问题是{instruction}'),
        ('ai','我是你的个人助手,我将尽我所能回答问题')
    ]
)

str1 = prompt_template.format(uname='小言',instruction='土星有几个卫星')
print(type(str1))
print(str1)

#tips:字符串形式
prompt_template1 = ChatPromptTemplate(
    messages=[
        '你叫{uname}' #tips:等价于('human','你叫{uname}')
    ]
)

str2 = prompt_template1.format(uname='小明')
print(type(str2))
print(str2)
#tips:字典形式
prompt_template2=ChatPromptTemplate(
    messages=[
        {'role':'system','content':'你叫{uname}'},
        {'role':'human','content':["复杂内容",{'type':'text'}]}
    ]
)

str2=prompt_template2.format(uname='小红')
print(type(str2))
print(str2)


#tips:内嵌ChatPromptTemplate

prompt_template3=ChatPromptTemplate(
    messages=[
        ('system','你是一个小说家')
    ]
)
prompt_template4=ChatPromptTemplate(
    messages=[
        ('human','写一篇300字内{novel_type}类型的小说')
    ]
)

prompt_template5 = ChatPromptTemplate.from_messages(
    [
        prompt_template3,
        prompt_template4
    ]
)

str5 = prompt_template5.format(
    novel_type='科幻'
)
print(type(str5))
print(str5)
'''
<class 'str'>
System: 你是一个小说家
Human: 写一篇科幻类型的小说
'''


resp = model.invoke(str5)
print(resp)
'''
content='最后一批人类上传意识至云端，肉体化为数据尘埃。
\n\n阿哲是其中一员。在虚拟世界里，没有饥饿，没有衰老，
永恒的和平让他感到前所未有的空虚。他开始怀念阳光的温度、雨水的味道，甚至泥土的芬芳。
\n\n一天，他在数据流深处发现了一行被遗忘的代码：一个模拟地球生态系统的程序。他激活了它。
\n\n虚拟的星球上，第一次长出了青草。阿哲脱掉数据化的鞋，光脚踩在柔软的草地上。他仰头，看着数据模拟的、却无比真实的星空，流下了第一滴眼泪。在这里，
他终于找到了永恒的意义。' 
additional_kwargs={'refusal': None} 
response_metadata={'token_usage': {'completion_tokens': 136, 'prompt_tokens': 26, 'total_tokens': 162, 
'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_provider': 'openai', 'model_name': 'glm-4', 
'system_fingerprint': None, 'id': '20260325111134de9839fa3ac14f0f', 'finish_reason': 'stop', 'logprobs': None} 
id='lc_run--019d22f9-e067-7622-96d1-84ca9caae1fb-0' tool_calls=[] invalid_tool_calls=[] usage_metadata={'input_tokens': 
26, 'output_tokens': 136, 'total_tokens': 162, 'input_token_details': {}, 'output_token_details': {}}
'''