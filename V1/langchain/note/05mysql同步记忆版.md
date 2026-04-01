## mysql保存记忆

## docker运行mysql
```shell
nikofox@MOSS:~$ docker run -d -p 63306:3306 -e MYSQL_ROOT_PASSWORD=xxxxxxx 24e4
52f0933f7f22871bea67edd096753f21769d2883a4dc683ac7a713f92237d29a

```
## 然后用beekeeper创建一个库并使用
![](./imgs/10.png)


## 接下来写代码

注意表名称不写的话默认就是message_store
```python
# @Time    : 2026/4/1 14:02
# @Author  : hero
# @File    : 27记忆缓存mysql版.py

from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory,RunnableConfig
from dotenv import load_dotenv
import os
from loguru import logger
load_dotenv()

langsmith_key =os.getenv('lang_smith_key')
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = f'{langsmith_key}'
zai_key = os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')

llm_zai = ChatOpenAI(
    model='glm-4',
    api_key=zai_key,
    base_url=zai_url,
    temperature=0.6,
    max_retries=2
)

prompt_template=ChatPromptTemplate(
    messages=[
        ('system','你现在是一名五星级大厨师'),
        MessagesPlaceholder(variable_name='history'),
        ('human','{user_input}')

    ]
)

parser = StrOutputParser()

chain = prompt_template|llm_zai|parser

# -------------从这里开始配置------------------------
mysql_url = f'mysql+pymysql://root:{os.getenv("MYSQL_DOCKER")}@127.0.0.1:63306/mem_llm'
def get_session_history(session_id:str):
    return SQLChatMessageHistory(
        session_id,
        connection=mysql_url,
        table_name='message_store',
    )
chain_with_history=RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key='user_input',
    history_messages_key='history'
)
# -------------------------------------------
config=RunnableConfig(
    configurable={
        'session_id':'chat_1'
    }
)

def chat_loop():
    print('\n👨‍🍳 新东方超级大厨已启动,输入"quit"退出')
    while True:
        user_quiz= input('\n输入你的问题>').strip()
        if user_quiz.lower()=='quit':
            break
        try:
            result = chain_with_history.invoke({'user_input':user_quiz},config)
            if result:
                print(f'👨‍🍳{result}\n')
        except Exception as e:
            logger.error(f'\n出错了⚠️:{e}')


    #tips:清理
    logger.info('谢谢您的提问!🎉')


if __name__ == '__main__':
    chat_loop()
```

**注意mysql引擎默认是同步的,所以只好同步**

## 对话完之后看看数据库中有没有内容
![](./imgs/11.png)


## 测试长期记忆
```shell
/home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/V1/langchain/code/27记忆缓存mysql版.py 

👨‍🍳 新东方超级大厨已启动,输入"quit"退出

输入你的问题>我之前问你要做什么菜来着?
👨‍🍳
您之前问的是**糖醋里脊**的做法。我已经为您提供了详细的制作步骤，包括食材准备、腌制、裹粉、炸制、调制糖醋汁以及最后的调味和装盘技巧。

如果您想重新回顾糖醋里脊的做法，或者想了解其他菜谱，请随时告诉我！我可以为您提供更多美食建议或烹饪技巧。


输入你的问题>
```