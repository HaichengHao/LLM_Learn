# @Time    : 2026/4/9 10:33
# @Author  : hero
# @Modified by: assistant
# @File    : 31小案例_gradio.py

import asyncio
import gradio as gr
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv
from loguru import logger
import os

load_dotenv()
langsmith_key = os.getenv('lang_smith_key')
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

prompt_template = ChatPromptTemplate(
    messages=[
        ('system', '你现在是一名五星级大厨师'),
        MessagesPlaceholder(variable_name='history'),
        ('human', '{user_input}')
    ]
)

parser = StrOutputParser()

chain = prompt_template | llm_zai | parser

REDIS_DB_URL = 'redis://127.0.0.1:65522/6'


def get_session_history(session_id: str) -> RunnableWithMessageHistory:
    return RedisChatMessageHistory(
        session_id=session_id,
        url=REDIS_DB_URL,
        ttl=360  # tips:保存六分钟记录
    )


chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    history_messages_key='history',
    input_messages_key='user_input',
)

#tips:之前的config
# config=RunnableConfig(
#     configurable={
#         'session_id':'chat_1'
#     }
# )


#tips:之前的chat_loop
async def chat_loop():
    """保持原有的命令行版本"""
    print('\n👨‍🍳 新东方超级大厨已启动,输入"quit"退出')
    config = RunnableConfig(configurable={'session_id': 'chat_1'})
    while True:
        user_quiz = input('\n输入你的问题>').strip()
        if user_quiz.lower() == 'quit':
            break
        try:
            print('👨‍🍳', end='', flush=True)
            async for chunk in chain_with_history.astream({'user_input': user_quiz}, config):
                print(chunk, end='', flush=True)
            print('\n')
        except Exception as e:
            logger.error(f'\n出错了⚠️:{e}')

    logger.info('谢谢您的提问!🎉')



# 定义异步聊天函数，支持流式输出
async def predict_async(message, history):
    """处理用户消息并生成流式响应"""
    # 使用固定的会话ID，实际应用中可以根据用户动态生成
    config = RunnableConfig(configurable={'session_id': 'chat_1'})

    # important：初始化累积响应，之后用生成器输出它
    full_response = ""

    # 使用 astream 进行异步流式处理
    async for chunk in chain_with_history.astream(
            {'user_input': message},
            config
    ):
        full_response += chunk
        # 使用 yield 返回部分结果，实现流式输出
        await asyncio.sleep(0.01)  # 添加短暂延迟使流式效果更明显
        yield full_response #important:使用生成器生成,实现流式对话



if __name__ == '__main__':
    #之前用chat_loop的话就是
    # asyncio.run(chat_loop())
    # 使用 ChatInterface 创建聊天界面，启用流式输出
    demo = gr.ChatInterface(
        fn=predict_async,  # 使用异步函数
        title="👨‍🍳 五星级大厨聊天机器人",
        description="我现在是一名五星级大厨，有什么烹饪问题可以问我！",
        examples=["如何煎牛排？", "怎样做糖醋里脊？", "怎么煮咖啡？"],
        multimodal=False,  # 禁用多模态输入

    )

    demo.launch(
        server_name="127.0.0.1",  # 本地运行
        server_port=7860,  # 端口
        share=False,  # 是否创建公共链接
        debug=True,  # 调试模式
    )