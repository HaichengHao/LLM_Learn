# @Time    : 2026/3/22 12:01
# @Author  : hero
# @File    : demo1.py
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv('api_key')
openai_base_url=os.getenv('base_url')
mysql_pwd = os.getenv('mysqlpwd')

#step 1创建大模型
MODEL_NAME='gpt-4o-mini'
openai_llm = ChatOpenAI(
    model=MODEL_NAME,
    api_key=openai_api_key,
    base_url=openai_base_url,
    temperature=1.0,
    max_tokens=400,
    max_retries=2
)

#tips:或者这样定义
open_ai_llm =init_chat_model(
    model=MODEL_NAME,
    model_provider='openai',
    api_key=openai_api_key,
    base_url=openai_base_url,
    temperature=1.0
)

#step 2  创建提示词模板

#important:上下文交互
# 我们要保存历史记录,那么有一个问题,我们要把它保存在哪里呢？一般存在数据库中
prompt = ChatPromptTemplate.from_messages(
    messages=[
        ('system','你是一个新东方厨师,只会做菜相关的知识,除此之外的你一概回答“我只是厨师,不知道别的领域的知识哦”'),
        MessagesPlaceholder(variable_name='history'), #important:这里传入历史记录
        ('user','{user_text}')
    ]
)
#step 3 解析器
parser = StrOutputParser()

#important:LCEL
chain = prompt|openai_llm|parser

#tips:把聊天记录存入数据库中
def get_session_history(sid):
    """
    根据会话ID来读取和保存历史记录,必须要BaseChatMessageHistory
    """
    return SQLChatMessageHistory(  #tips:可以看看源码,connection_string要求传入一个数据库链接
        session_id=sid,
        connection=f'mysql+pymysql://root:{mysql_pwd}@localhost:3306/llmdb',
    )




runnable = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key='user_text',
    history_messages_key='history'

)

# USER_TEXT = input('请输入您想问五星级大厨师的问题>>>')
# res = chain.invoke({'user_text':USER_TEXT})
# print(res)

#important:利用传入config来传入session_id,langchain会自动帮我们处理同一session_id的历史上下文

res1 = runnable.invoke(
    {'user_text':'椒麻鸡怎么做'},
    config={'configurable':{'session_id':'niko001'}}
)
print(res1)
print('---'*40)
# USER_TEXT2=input('请继续提问>>')
res2 = runnable.invoke(
    {'user_text':'没有麻椒用花椒替代可以么?'},
    config={'configurable':{'session_id':'niko001'}}
)
print(res2)

'''
/home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/v2langchain/code/demo1上下文.py 
/home/nikofox/LLMlearn/.venv/lib/python3.12/site-packages/langchain_core/runnables/history.py:596: LangChainDeprecationWarning: `connection_string` was deprecated in LangChain 0.2.2 and will be removed in 1.0. Use connection instead.
  message_history = self.get_session_history(
椒麻鸡是一道麻辣鲜香的美食，以下是椒麻鸡的简单做法：

### 材料：
- 鸡腿肉或整鸡：500克
- 姜：几片
- 大葱：1根
- 食盐：适量
- 料酒：1汤匙
- 辣椒粉：适量
- 花椒粉：适量
- 食用油：适量
- 生抽：适量
- 蒜末：适量
- 香葱：适量（用作装饰）

### 步骤：

1. **腌制鸡肉**：将鸡肉洗净切块，放入碗中，加入姜片、大葱、食盐、料酒，搅拌均匀后腌制30分钟。

2. **煮鸡肉**：腌制好的鸡肉放入锅中，加水没过鸡肉，烧开后撇去浮沫，转小火煮20分钟，直到鸡肉熟透。捞出鸡肉，沥干水分后自然冷却。

3. **调制椒麻油**：
   - 在一个小锅中，加入适量食用油，放入蒜末，煸炒出香味。
   - 然后加入适量的辣椒粉和花椒粉，炒出香味，油的颜色会变得鲜红。

4. **拌鸡肉**：将冷却后的鸡肉放入大碗中，加入生抽、用炒香的油和调料一起拌匀。

5. **装盘**：最后，装盘时可撒上一些香葱作为装饰增色。

这样，一道美味的椒麻鸡就完成了！你可以根据个人口味调整辣椒粉和花椒粉的用量。享用吧！
------------------------------------------------------------------------------------------------------------------------
可以的，花椒和麻椒在味道上有些相似，花椒也能带来麻辣的感觉。如果没有麻椒，用花椒替代的话，椒麻鸡依然会很好吃。你可以根据个人口味适量增加花椒的用量来增强麻味。希望你能做出美味的椒麻鸡！

Process finished with exit code 0

'''

# important：检查数据库，发现数据库也存入了会话记录,成功!!!