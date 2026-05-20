# @Time    : 2026/5/17 19:12
# @Author  : hero
# @File    : 07HITL初体验.py
from langchain_core.tools import tool
from langgraph.graph import StateGraph
from langgraph.types import Interrupt
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver
from pymysql import Connection
from langgraph.types import  Command


from dotenv import load_dotenv
import os


load_dotenv()


llm = init_chat_model(
    model='glm-4',
    model_provider='openai',
    api_key=os.getenv('zhipu_key'),
    base_url=os.getenv('zhipu_base_url')
)


# sql_client = Connection(
#     host='127.0.0.1',
#     port=3306,
#     user='root',
#     password=os.getenv('MYSQL_DOCKER'),
#     database=''
# )

#删除表工具
@tool
def del_table(table_name:str):
    """
    高危动作工具,删除传入的表
    :param table_name:
    :return:
    """
    #伪代码
    print(f'【调用了删除表的工具】>>>删除了{table_name}表')

    return f'删除了表{table_name}'



#删除文件工具

@tool
def del_file(file_name:str):
    """
    删除文件
    :param file_name:
    :return:
    """
    print(f'【调用了删除文件的工具】>>>删除了{file_name}文件')

    return f'删除了文件{file_name}'

#查询表数据工具

@tool

def select_database(table_name:str):
    """
    查询表数据
    :param table_name:
    :return:
    """
    print(f'【调用了查询数据的工具】>>>查询了{table_name}表!!')
    return f'查询了{table_name}的数据'


#创建deepagent,同时给高危工具设置人机交互!拦截动作

#1.必备内容,短期记忆+线程id，就像之前学langgraph高级特性中的state_persistant一样

check_pointer = InMemorySaver()
config = {"configurable": {"thread_id": "user_nikofox1212"}}

#创建agent,设置高危工具需要拦截处理

main_agent=create_deep_agent(
    model=llm,
    tools=[select_database,del_file,del_table],
    system_prompt="回答使用中文,调用对应的工具实现对应的功能!",
    #step 创建中断条件
    interrupt_on={
        "del_table":True,#通过/编辑/拒绝
        "del_file":True,#通过/编辑/拒绝
        "select_database":False,#这里意思就是你查数据不用请求我的同意
        #tips:或者还有这种写法: 'delete_file":["approve","reject","edit"] 这样用列表指定自己想用的操作
    },
    checkpointer=check_pointer,

)


#step 预执行,本次不会真正的执行,所有都不会执行,判定本次执行链中是否存在人机交互节点,存在需要设置后二次执行

result_1=main_agent.invoke(
    {
        "messages":[
            {
                'role':'user',
                'content':'查询一下product表的数据;再删除user表,最后删除haha.txt文件'
            }
        ]
    },
    config=config
)


#检查本次执行是否存在人机交互动作 important:如果有人机交互动作,会将交互的拦截点信息存储到__interrupt__中
interrupt = result_1['__interrupt__']
# print(interrupt)

'''
[Interrupt( ->Interrupt对象
    value={ ->value属性
        'action_requests':  ->列表,存储了本次触发的拦截的工具信息(名字和参数)
            [
                {
                'name': 'del_table', 
                'args': {'table_name': 'user'}, 
                'description': "Tool execution requires approval\n\n
                                Tool: del_table\n
                                Args: {'table_name': 'user'}"}, 
                {
                'name': 'del_file', 
                'args': {'file_name': 'haha.txt'},
                'description': "Tool execution requires approval\n\n
                                Tool: del_file\n
                                Args: {'file_name': 'haha.txt'}"
                                }
                                ], 
                'review_configs': [
                    {'action_name': 'del_table', 
                    'allowed_decisions': ['approve', 'edit', 'reject']}, 
                    {'action_name': 'del_file', 
                    'allowed_decisions': ['approve', 'edit', 'reject']}]}, 
                id='71a618960338eeb13c0e957f54422038')]
'''
#tips:上面都是预先执行
if interrupt:
    #处理人机交互动作,二次执行
    #输出一共有几个工具被拦截了,这些工具的名字是什么
    actions = interrupt[0].value['action_requests']
    print(
        f"本次需要审核工具数量:{len(actions)},\n "
        f"具体拦截的工具有{[action['name'] for action in actions ]}"
    )
    '''
        本次需要审核工具数量:2,
     具体拦截的工具有['del_table', 'del_file']
    '''
    #审批意见
    decisions=[]
    for action in actions:
        action_name = action['name']
        action_args = action['args']
        #检查代码,是approve,edit,还是reject
        if action_name == 'del_table':
            #拦截
            #每一次拦截的动作{'type':'reject|approve'}
            #important:按照decisions的元素的顺序进行拦截还是执行,因为最终还是根据action_requests的动作来决定顺序的!!
            decisions.append({'type':'reject'})
        elif action_name == 'del_file':
            decisions.append({'type':'approve'})
    #tips:二次执行(真执行) 不需要传入用户的query ; 第二次的thread_id必须等与第一次的thread_id,
    # 审批意见传递用的是Command(之前在LangGraph中学过可以用来更新参数和跳跃节点)
    result_2 = main_agent.invoke(
        #传入审批意见，再次执行
        Command(
            resume={
                'decisions':decisions,
            }
        ),
        config=config
    )

    # print(f"最终结果{result_2['messages'][-1].pretty_print()}")
    print(f"最终结果{result_2['messages'][-1].content}")
    ''' 
    【本次需要审核工具数量:2,
     具体拦截的工具有['del_table', 'del_file']
    【调用了查询数据的工具】>>>查询了product表!!
    【调用了删除文件的工具】>>>删除了haha.txt文件
    最终结果
    已完成以下操作：
    
    1. ✅ 查询了product表的数据
    2. ❌ 删除user表操作被用户拒绝
    3. ✅ 删除了haha.txt文件
    
    用户拒绝了删除user表的请求，但product表数据查询和haha.txt文件删除都已成功完成。'''
    #因为给del_table的type是reject,所以拒绝了这一操作,且删除文件操作允许了