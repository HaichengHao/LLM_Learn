# @Time    : 2026/5/20 10:29
# @Author  : hero
# @File    : 15使用skill.py

'''


注意事项:
1.先配置filebackend再配置skills属性,相对于file_backend的目录下 存储skill技能文件夹的名称
2.skills的文件夹名称必须等于SKILL.md yaml中的name
3.SKILL渐进式加载,模型先加载SKILL元数据,yaml数据,根据需求再加载下面的提示词中的md,
预加载(启动时加载)->调用时加载->按需加载,三层披露
元数据要有name和description

4.不是SKILL越多越好,基本是7-10,多了模型也不调用,千万不要放重复功能的SKILL,否则它会选不出来
5.测试好SKILL触发的提示词
'''



from pathlib import Path
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend,StateBackend,StoreBackend,CompositeBackend
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from loguru import logger
import os
load_dotenv()

llm = init_chat_model(
    model='glm-4',
    model_provider='openai',
    api_key=os.getenv('zhipu_key'),
    base_url=os.getenv('zhipu_base_url')
)


#step 1.创建fileSystemBackend通过设置skill技能所在的文件夹
current_dir = Path(__file__).parent.resolve() #读取到当前文件所在的文件夹
file_backend = FilesystemBackend(
    root_dir=current_dir,
    virtual_mode=True,
)


#step 2 创建deepagent并且设置skill技能所在的文件夹(相对于file_backend的目录下)

main_agent = create_deep_agent(
    model=llm,
    backend=file_backend,
    skills=[
        "skills" #想对于file_backend的目录下存储skill技能文件夹的名称
    ],
    checkpointer=InMemorySaver(),
    system_prompt="你是一个智能助手,可以使用技能"
)

config={
    'configurable':{
        'thread_id':'demo1'
    }
}
# result = main_agent.invoke(
#     {
#         'messages':{
#             'role':'user',
#             'content':'你帮我罗列一下你有什么技能'
#         }
#     },
#     config=config
# )
#
# print(result['messages'][-1].content)

'''

我可以使用的技能如下：

1. **code-reviewer** - 代码审查技能
   - 当用户请求进行代码审查(Code Review)或寻找代码Bug时使用
   - 读取路径：`/skills/code-reviewer/SKILL.md`

2. **emoji-translator** - 表情符号翻译技能
   - 将用户的文本翻译成表情符号(Emoji)，或者将表情符号翻译成文字
   - 用于增加对话的趣味性
   - 读取路径：`/skills/emoji-translator/SKILL.md`

3. **session-logs** - 会话日志分析技能
   - 搜索和分析自己的会话日志（较早的/父级对话）使用jq
   - 读取路径：`/skills/session-logs/SKILL.md`

除了这些专门技能外，我还具备以下核心能力：

- 文件系统操作（读取、编辑、创建文件和目录）
- 搜索和查找文件内容
- 执行复杂的多步任务
- 使用子代理处理独立的复杂任务
- 任务管理和进度跟踪

如果您需要了解某个特定技能的详细使用方法，我可以读取相应的技能文档为您提供完整说明。
'''
query1="我早上起床晚了,赶公交车差点摔倒，还好最后到了公司,使用emoji-translator技能翻译"
result = main_agent.invoke(
    {
        'messages':{
            'role':'user',
            'content':query1
        }
    },
    config=config
)

print(result['messages'][-1].content)
'''

😴🌅⏰🏃‍♂️💨🚌🤕🏃‍♂️💨🏢✅'''