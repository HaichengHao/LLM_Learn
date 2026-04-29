# @Time    : 2026/4/29 11:42
# @Author  : hero
# @File    : 02流式处理.py
'''
本节详细讲解流式处理
'''

from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
from deepagents import create_deep_agent
from dotenv import load_dotenv
from typing import Literal
import os


load_dotenv()

tavily_content = TavilyClient(os.getenv('TAVILY_API_KEY'))


def init_model():
    # return init_chat_model(
    #     model='glm-4',
    #     model_provider='openai',
    #     api_key=os.getenv('zhipu_key'),
    #     base_url=os.getenv('zhipu_base_url')
    # )

    return ChatOpenAI(
        model='glm-4',
        api_key=os.getenv('zhipu_key'),
        base_url=os.getenv("zhipu_base_url")
    )


def internet_search(
        query: str,
        max_results: int = 3,
        topic: Literal['general', 'news', 'finance'] = 'general',
        include_raw_content: bool = False,
):
    """
    run a web search tool
    :param query:
    :param max_results:
    :param topic:
    :param include_raw_content:
    :return:
    """
    return tavily_content.search(
        query=query,
        max_results=max_results,
        topic=topic,
        include_raw_content=include_raw_content
    )


research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

agent = create_deep_agent(
    model=init_model(),
    tools=[internet_search],
    system_prompt=research_instructions
)

#=============================================================================#
'''#使用流式调用
for chunk in  agent.stream(
        {
            "messages":[
                {"role": "user",
                 "content": "今天沈阳的天气如何?"}
            ]
        },
    # stream_mode="messages" #tips：开启后返回的结果将会是(chunk:BaseMessagesChunk,metadata:dict)元组,不开启的话返回的将会是字典
):
    print(chunk)

'''

'''
可以看到第一条是中间件,之后也会学到这个概念,但是目前要做的是处理掉它
{'PatchToolCallsMiddleware.before_agent': {'messages': Overwrite(value=[HumanMessage(content='今天沈阳的天气如何?', additional_kwargs={}, response_metadata={}, id='7b367d87-17c2-4dff-938b-5c691fe220fa')])}}
{'model': 
    {'messages': [AIMessage(content='\n我来帮您查询沈阳今天的天气情况。\n', 
                    additional_kwargs={'refusal': None}, 
                    response_metadata={'token_usage': {'completion_tokens': 35, 'prompt_tokens': 6032, 'total_tokens': 6067, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_provider': 'openai', 'model_name': 'glm-4', 'system_fingerprint': None, 'id': '20260429120402b36207ce0c5c4fa9', 
                    'finish_reason': 'tool_calls',⚠️ 'logprobs': None},
                    id='lc_run--019dd768-795f-7b00-b285-5e31341db350-0',
                    tool_calls=[{'name': 'internet_search', ⚠️⚠️⚠️⚠️⚠️
                                'args': {'query': '沈阳今天天气', 'max_results': 3}, 
                                'id': 'call_-7667605380389664477', 'type': 'tool_call'}], 
                                invalid_tool_calls=[], usage_metadata={'input_tokens': 6032, 'output_tokens': 35, 'total_tokens': 6067, 'input_token_details': {}, 'output_token_details': {}})]}}
{'TodoListMiddleware.after_model': None}
{'tools': 
    {'messages': [
        ToolMessage(
                content='{
                    "query": "沈阳今天天气", 
                    "follow_up_questions": null,
                    "answer": null, "images": [],
                    "results": [
                    {"url": "http://wap.weather.com.cn/e_index/sudutianqi.html?aid=101070101", "title": "沈阳今日天气", "content": "今晨6时，沈阳晴，气温2℃，西南风4-5级，相对湿度97%。 预计，今天白天多云，最高气温10℃，西风3-4", "score": 0.99993443, "raw_content": null}, 
                    {"url": "http://weathernew.pae.baidu.com/weathernew/pc?query=%E8%BE%BD%E5%AE%81%E6%B2%88%E9%98%B3%E5%A4%A9%E6%B0%94&srcid=4982&city_name=%E6%B2%88%E9%98%B3&province_name=%E8%BE%BD%E5%AE%81", "title": "沈阳 - 百度", "content": "沈阳 今天：阴 7°~18°C 东北风4级. 04月27日 周一 农历三月十一. 7°. 45 优. 阴 东北 ... 生活气象指数 早上好，天气不好，也记得让心情保持舒畅哦. 穿衣: 大衣类. 7", "score": 0.99992454, "raw_content": null},
                    {
                    "url": "https://m.sy.bendibao.com/tianqi/today.shtm", "title": "今日沈阳天气预报查询", "content": "辽宁沈阳今日天气详情 · 今天天气 · 明天天气 · 一周天气 · 10天天气 · 15天天气 · 空气质量. 沈阳今天天气. 白天. 多云. 最高：29℃. 夜间. 多云. 最低：17℃.", "score": 0.9998591, "raw_content": null}], "response_time": 0.95, "request_id": "ffb2128e-9f81-4b87-a35f-6afc7d9f0f48"}', 
                    name='internet_search',⚠️
                    id='049a12a0-740a-47b6-99b5-bd21b9adb1f2', tool_call_id='call_-7667605380389664477')]
                    }
                    }
{'model': {'messages': [
        AIMessage(
            content='\n根据搜索结果，沈阳今天的天气情况如下：\n\n**沈阳今日天气：**\n- **天气状况**：多云\n- **气温范围**：7°C - 18°C\n- **风向风力**：东北风4级\n- **空气质量**：优（AQI 45）\n\n**生活建议：**\n- 穿衣建议：大衣类\n- 整体天气较为舒适，但风力较大，外出时注意防风', 
            additional_kwargs={'refusal': None}, 
            response_metadata={'token_usage': {'completion_tokens': 94, 'prompt_tokens': 6553, 'total_tokens': 6647, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 
            'model_provider': 'openai', 'model_name': 'glm-4', 'system_fingerprint': None, 
            'id': '202604291204257568c6b5c4d24134', 'finish_reason': 'stop', 'logprobs': None},
            id='lc_run--019dd768-d79f-7ca2-a845-caf843f58f84-0',
            tool_calls=[], ⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️  最后一条tool_calls为空
            invalid_tool_calls=[], 
            usage_metadata={'input_tokens': 6553, 
            'output_tokens': 94, 'total_tokens': 6647, 
            'input_token_details': {}, 'output_token_details': {}})]}}
{'TodoListMiddleware.after_model': None}
'''

#=============================================================================#

# 可以看到返回的结果如果没指定stream_mode的话那么默认返回的是一个个字典,有model有tool,后面跟着的是messages
#tips:处理掉中间件信息
inputs= {
            "messages":[
                {"role": "user",
                 "content": "今天沈阳的天气如何?"}
            ]
        }
for chunk in agent.stream(
        inputs
):
    for node_name,state in chunk.items(): #tips:.item是为了获取字典的键和值
        #避开中间件数据的干扰
        #如果state为None或者没有messages属性就不处理
        if not state or "messages" not in state:continue

        #获取本次的消息信息集合

        #一般是这么取,但是不够健壮
        # messages=state["messages"][-1].content.pretty_print()

        #tips:要判断messages是否为空并且判断是它的值是否是一个列表
        messages=state['messages']
        if messages and isinstance(messages,list):
            #tips:如果非空且值是列表的话就取出其中最后一条(一般是AIMessages)的content(回复内容)
            last_msg=messages[-1]

            #tips:如果是模型节点
            if node_name == "model":
                #三种,调用了模型;大模型调用了工具/subagent;直接最终的返回结果
                if last_msg.tool_calls:#important:如果tool_calls有值,说明这个模型消息是调用工具的模型消息,表明是在工具调用前,接下来将会是tool节点,再次才是回到model节点
                    #判断调用了大模型,大模型决定调用哪个工具,或者调用哪个subagent
                    for tool_call in last_msg.tool_calls: #tips:tool_calls是一个列表
                        if tool_call['name']=='task': #important:如果工具调用的name是task则说明其调用了子智能体,子智能体中有一个形如
                            '''子智能体的调用中的tool_calls和单纯工具调用是有不同之处的
                            来对比一下
                            
                            #=====普通工具=======
                            tool_calls=[{'name': 'internet_search', ⚠️⚠️⚠️⚠️⚠️
                                'args': {'query': '沈阳今天天气', 'max_results': 3}, 
                                'id': 'call_-7667605380389664477', 'type': 'tool_call'}],
                                
                                
                            #=====子智能体======
                            tool_calls=[
                                {
                                    "name":"task",
                                    "args":{
                                        "subagent_type":"网络搜索助手",#目标子agent
                                        "description":"咨询2026政策"
                                    }
                                }
                            ]
                            '''
                            #调用子智能体
                            print(f'<大模型>决定调用子智能体:{tool_call['args']['subagent_type']}')
                        else:
                            #决定调用哪个工具
                            print(f'<大模型>决定调工具:{tool_call['name']}传入的参数:{tool_call['args']}')

                elif last_msg.content: #important:如果tool_calls为空,说明已经调取tool结束了,是发生在工具节点之后
                    print(f'最终执行的结果:{last_msg.content}')

            #tips:如果是工具节点
            elif node_name == "tools":
                #一种类型,agent要调用具体的工具了!!工具返回了具体的结果
                tool_return_result = last_msg.content
                tool_name=last_msg.name
                print(f'<agent>调用了{tool_name}工具,返回的结果是{tool_return_result}')
print(agent.get_graph().print_ascii()) #important:由于create_agent抑或是create_deep_agent本身都是基于langgraph的设计范式,返回的是一个编译好的图,所以我们可以可视化图来查看,还有记得多智能体supervisor返回的是一个状态图但是未编译,需自己.compile()编译
with open('../graph_out/stream_output_1.png', 'wb') as f:
    f.write(agent.get_graph().draw_mermaid_png())
    print('保存agent图成功')


# step 运行看看结果
'''
/home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/V1/DeepAgents/code/02流式处理.py 
<大模型>决定调工具:internet_search传入的参数:{'query': '沈阳今天天气 天气预报', 'max_results': 3}
<agent>调用了internet_search工具,返回的结果是{"query": "沈阳今天天气 天气预报", "follow_up_questions": null, "answer": null, "images": [], "results": [{"url": "https://www.weather.com.cn/weather/101070101.shtml", "title": "沈阳天气预报,沈阳7天天气预报,沈阳15天天气预报,沈阳天气查询", "content": "# 19日（今天）. # 20日（明天）. # 21日（后天）. # 22日（周三）. # 23日（周四）. # 24日（周五）. # 25日（周六）. ### 蓝天预报综合天气现象、能见度、空气质量等因子，预测未来一周的天空状况。. 辐射较弱，涂擦SPF12-15、PA+护肤品。. # 天气资讯. # 周边地区 *|* 周边景点 *2026-04-19 18:00更新*. # 周边地区 *|* 周边景点 *2026-04-19 18:00更新*. # 高清图集. # 重大天气事件. ## 我国降水将增多增强 北方多地有大风沙尘天气. 今天（4月19日），南方将自西向东迎来新一轮降雨过程。同时，北方降水也将增多，受强冷空气影响，多地有大风沙尘天气，气温也会陆续下降。. ## 北方多地气温冲击30℃ 明起冷空气携降温雨雪影响中东部. 今天（4月18日），南方降雨将进一步减弱，江南多地有望迎来放晴，北方多地气温将会冲击30℃。不过，明天起中东部地区将出现大范围降雨过程。. ## 南方降雨即将减弱南压 江南至北方多地暖热将至. 今天（4月16日），南方部分地区雨势较强，并伴有强对流天气，需注意防范。明后天，南方降雨减弱、南压。. ## 南方新一轮降雨过程来袭 东北至江南本周后期升温明显. 今起三天（4月15日至17日），南方将迎新一轮降雨过程，并伴有强对流天气，同时北方地区也将自西向东迎来较大范围降水。. ## 南方大范围降雨持续 北方多地气温波动中上升. 今起三天（4月14日至16日），南方大部继续维持多雨格局，并伴有强对流天气。在北方，东北、华北、黄淮等地有降雨出没，大部地区气温将在波动中上升。. ## 未来三天江南维持多雨模式 华南炎热不减多地气温或破纪录. 未来三天（4月13日至15日），南方主雨带仍将维持在江南地区，16日开始将有所南压。同时，华南天气持续炎热，公众需持续做好防暑降温措施。. ## 南方降雨范围仍然较大 中东部多地气温波动起伏. 未来三天，南方降雨范围较大，降雨强度较前期明显减弱。受阴雨和冷空气影响，东北、华北一直到江南多地明后天将现降温，之后气温再度回升。. ## 江南降雨连连部分地区有暴雨 华北多地气温将创新高. 今明天，江南等地部分地区仍是降雨连连，需防范次生灾害的发生。华南炎热天气仍将持续，部分地区有高温天气，北方气温多起伏。. ## 江南多地有暴雨伴强对流 华南局地或上演“高温连续剧”. 今天（4月9日），南方核心降雨区仍偏北，长江中下游多地有强降雨。明天将南落至江南中南部地区，江西、湖南等地雨势增强。. ## 长江中下游多地有强降雨伴强对流 华南局地或现连续性高温. 今明天（4月8日至9日），南方将迎新一轮降雨过程，此轮降雨主雨带将明显北抬至长江中下游地区。江南南部、华南等地热力将升级，公众需注意防暑降温。. ## 今夜起强降雨区将北抬至长江中下游 华南高温冒头需防暑. 未来三天（4月7日至9日），南方仍将处多模式，今夜起强降雨区域将转移至长江中下游地区，局地有暴雨或大暴雨，公众需关注预警预报信息，注意交通安全。. ## 今天南方雨势仍强东北雨雪持续 未来一周中东部气温波动频繁. 今明两天（4月6日至7日），南方大范围降雨将持续，其中今天雨势仍然较强；同时，东北地区依然有大范围雨雪，部分地区或现暴雪。. ## 南方降雨再度增多局地或现暴雨 北方迎显著降温东北雨雪持续. 清明假期后两日，南方降雨将再度增多，江南、华南等地或现暴雨，同时北方将现显著降温，其中东北地区大范围雨雪持续，黑龙江局地有暴雪。. # 雷达图. # 联播天气预报. # 更多>>高清图集. # 天气视频. # >> 生活旅游. ### 景点推荐. #### 景区天气气温 旅游指数. # 气象产品. # 气象服务. # 天气预报电话查询. # 手机查询. ### 网站服务. ### 营销中心. ### 相关链接. 客服邮箱：service@weather.com.cn客服电话：**010-68409444**京ICP证010385-2号　京公网安备11041400134号.", "score": 0.79022324, "raw_content": null}, {"url": "https://www.ventusky.com/zh-tw/shenyang", "title": "天氣 - 沈阳 - 14天預報：氣溫、風和雷達 | Ventusky", "content": "| 晴朗的天空 15 °C 0 mm 0 %  西南  13 km/h | 晴朗的天空 18 °C 0 mm 0 %  西南  13 km/h | 晴朗的天空 19 °C 0 mm 0 %  西南  13 km/h | 晴朗的天空 21 °C 0 mm 0 %  西南  13 km/h | 晴朗的天空 22 °C 0 mm 0 %  西  14 km/h | 晴朗的天空 22 °C 0 mm 0 %  西  14 km/h | 晴朗的天空 23 °C 0 mm 0 %  西  14 km/h | 晴朗的天空 22 °C 0 mm 0 %  西  11 km/h | 晴朗的天空 22 °C 0 mm 0 %  西  9 km/h | 晴朗的天空 21 °C 0 mm 0 %  西南  7 km/h | 晴朗的天空 20 °C 0 mm 0 %  西南  8 km/h | 晴朗的天空 18 °C 0 mm 0 %  西南  10 km/h | 晴朗的天空 16 °C 0 mm 0 %  西南  10 km/h | 晴朗的天空 15 °C 0 mm 0 %  西南  10 km/h | 晴朗的天空 14 °C 0 mm 0 %  西南  9 km/h | 晴朗的天空 12 °C 0 mm 0 %  西南  8 km/h | 晴朗的天空 12 °C 0 mm 0 %  南  7 km/h | 晴朗的天空 11 °C 0 mm 0 %  南  5 km/h | 晴朗的天空 11 °C 0 mm 0 %  南  3 km/h | 晴朗的天空 11 °C 0 mm 0 %  南  3 km/h | 晴朗的天空 11 °C 0 mm 0 %  東南  4 km/h | 晴朗的天空 11 °C 0 mm 0 %  東南  4 km/h | 晴朗的天空 14 °C 0 mm 0 %  東南  4 km/h | 晴朗的天空 16 °C 0 mm 0 %  東南  8 km/h | 晴朗的天空 19 °C 0 mm 0 %  南  9 km/h |.", "score": 0.76701033, "raw_content": null}, {"url": "https://www.msn.com/zh-cn/weather/forecast/in-%E8%BE%BD%E5%AE%81%E7%9C%81,%20%20%20%20%20%E6%B2%88%E9%98%B3%E5%B8%82", "title": "辽宁省, 沈阳市天气预报 - MSN", "content": "大部晴朗. 风速. 24 公里/小时 · 湿度. 59% · 能见度. 16 公里 · 气压. 1014 hPa · 露点. 7°. 今天. 每小时预报 · 15° 14° 11° 10° 9° 8° 7° 8° 11° 13° 15° 17° 16° 15°", "score": 0.76512027, "raw_content": null}], "response_time": 0.83, "request_id": "f232cbe7-5190-4931-81a0-f86a41f705cf"}
最终执行的结果:
根据搜索结果，今天（4月19日）沈阳的天气情况如下：

**天气状况**：晴朗
**气温**：约15°C左右
**风力**：西南风，约13公里/小时
**湿度**：约59%
**能见度**：16公里

总体来说，今天沈阳天气晴朗，温度适宜，是个不错的天气。建议外出时可以适当增减衣物，注意防晒。

                           +-----------+                
                           | __start__ |                
                           +-----------+                
                                 *                      
                                 *                      
                                 *                      
             +---------------------------------------+  
             | PatchToolCallsMiddleware.before_agent |  
             +---------------------------------------+  
                                 *                      
                                 *                      
                                 *                      
                             +-------+                  
                             | model |                  
                           **+-------+...               
                         **              ...            
                      ***                   ..          
                    **                        ...       
+--------------------------------+               ..     
| TodoListMiddleware.after_model |                .     
+--------------------------------+                .     
                 .             .......            .     
                 .                    .....       .     
                 .                         ....   .     
            +---------+                      +-------+  
            | __end__ |                      | tools |  
            +---------+                      +-------+  
Process finished with exit code 0
'''

#==========================================================================================================#

#tips:不同的写法返回不同的类型,不同的类型有不同的获取消息的方式!!!!⚠️⚠️⚠️⚠️⚠️⚠️⚠️
# tips:如果指定为messages模式之后那么这个将返回一个元组(chunk,metadata)
'''for chunk in  agent.stream(
        {
            "messages":[
                {"role": "user",
                 "content": "沈阳故宫地址?"}
            ]
        },
    stream_mode="messages" #tips：开启后返回的结果将会是(chunk:BaseMessagesChunk,metadata:dict)元组,不开启的话返回的将会是字典
):
    print(chunk)'''

# important:可以看到下方对于chunk的输出,有的是(AIMessageChunk(),{metadata})如果调用了工具那就是(ToolMessageChunk(),{metadata})
'''
(AIMessageChunk(content='\n', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019dd76e-fd04-7eb2-bb1e-4f39eec19c71', tool_calls=[], invalid_tool_calls=[], tool_call_chunks=[]), {'ls_integration': 'langchain_chat_model', 'versions': {'deepagents': '0.5.3'}, 'lc_agent_name': None, 'langgraph_step': 2, 'langgraph_node': 'model', 'langgraph_triggers': ('branch:to:model',), 'langgraph_path': ('__pregel_pull', 'model'), 'langgraph_checkpoint_ns': 'model:93898834-f2c9-46d8-0bc3-1456bfc142e7', 'checkpoint_ns': 'model:93898834-f2c9-46d8-0bc3-1456bfc142e7', 'ls_provider': 'openai', 'ls_model_name': 'glm-4', 'ls_model_type': 'chat', 'ls_temperature': None})
(AIMessageChunk(content='', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019dd76e-fd04-7eb2-bb1e-4f39eec19c71', tool_calls=[{'name': 'internet_search', 'args': {'query': '沈阳故宫地址 地址', 'max_results': 3}, 'id': 'call_8decdd0ac8b3432f935b5d5c', 'type': 'tool_call'}], invalid_tool_calls=[], tool_call_chunks=[{'name': 'internet_search', 'args': '{"query":"沈阳故宫地址 地址","max_results":3}', 'id': 'call_8decdd0ac8b3432f935b5d5c', 'index': 0, 'type': 'tool_call_chunk'}]), {'ls_integration': 'langchain_chat_model', 'versions': {'deepagents': '0.5.3'}, 'lc_agent_name': None, 'langgraph_step': 2, 'langgraph_node': 'model', 'langgraph_triggers': ('branch:to:model',), 'langgraph_path': ('__pregel_pull', 'model'), 'langgraph_checkpoint_ns': 'model:93898834-f2c9-46d8-0bc3-1456bfc142e7', 'checkpoint_ns': 'model:93898834-f2c9-46d8-0bc3-1456bfc142e7', 'ls_provider': 'openai', 'ls_model_name': 'glm-4', 'ls_model_type': 'chat', 'ls_temperature': None})
(AIMessageChunk(content='', additional_kwargs={}, response_metadata={'finish_reason': 'tool_calls', 'model_name': 'glm-4', 'model_provider': 'openai'}, id='lc_run--019dd76e-fd04-7eb2-bb1e-4f39eec19c71', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 6030, 'output_tokens': 27, 'total_tokens': 6057, 'input_token_details': {}, 'output_token_details': {}}, tool_call_chunks=[]), {'ls_integration': 'langchain_chat_model', 'versions': {'deepagents': '0.5.3'}, 'lc_agent_name': None, 'langgraph_step': 2, 'langgraph_node': 'model', 'langgraph_triggers': ('branch:to:model',), 'langgraph_path': ('__pregel_pull', 'model'), 'langgraph_checkpoint_ns': 'model:93898834-f2c9-46d8-0bc3-1456bfc142e7', 'checkpoint_ns': 'model:93898834-f2c9-46d8-0bc3-1456bfc142e7', 'ls_provider': 'openai', 'ls_model_name': 'glm-4', 'ls_model_type': 'chat', 'ls_temperature': None})
(AIMessageChunk(content='', additional_kwargs={}, response_metadata={}, id='lc_run--019dd76e-fd04-7eb2-bb1e-4f39eec19c71', tool_calls=[], invalid_tool_calls=[], tool_call_chunks=[], chunk_position='last'), {'ls_integration': 'langchain_chat_model', 'versions': {'deepagents': '0.5.3'}, 'lc_agent_name': None, 'langgraph_step': 2, 'langgraph_node': 'model', 'langgraph_triggers': ('branch:to:model',), 'langgraph_path': ('__pregel_pull', 'model'), 'langgraph_checkpoint_ns': 'model:93898834-f2c9-46d8-0bc3-1456bfc142e7', 'checkpoint_ns': 'model:93898834-f2c9-46d8-0bc3-1456bfc142e7', 'ls_provider': 'openai', 'ls_model_name': 'glm-4', 'ls_model_type': 'chat', 'ls_temperature': None})
(ToolMessage(content='{"query": "沈阳故宫地址 地址", "follow_up_questions": null, "answer": null, "images": [], "results": [{"url": "https://www.amap.com/place/B001809F61", "title": "沈阳故宫博物院- 沈阳市沈河区| 地址营业时间", "content": "沈阳故宫博物院位于沈阳市沈河区，详细地址：沈阳市沈河区沈阳路171号。在Amap查看沈阳故宫博物院的精确位置、周边设施、用户评价，获取最佳出行路线和实时导航服务，", "score": 0.9999658, "raw_content": null}, {"url": "https://www.sypm.org.cn/map.html", "title": "地理位置-沈阳故宫博物院", "content": "地址：中国辽宁省沈阳市沈河区沈阳路171号\u3000邮政编码：110011\u3000地铁站点：中街.", "score": 0.99986017, "raw_content": null}, {"url": "https://m.map.360.cn/m/search/detail/pid=b50545c110628e0d", "title": "【沈阳故宫】地址,电话,路线,周边设施", "content": "沈阳故宫位于辽宁省沈阳市沈河区沈阳路171号，始建于1625年，占地6万多平方米，建筑面积约9千平方米，是中国仅存的两大皇家宫殿建筑群之一，也是关外唯一的皇家建筑群，为国家一", "score": 0.9998579, "raw_content": null}], "response_time": 0.86, "request_id": "72bf1617-4d9a-4c41-a019-7e13527da466"}', name='internet_search', id='af6b703e-6436-456e-8a46-17c320df03b1', tool_call_id='call_8decdd0ac8b3432f935b5d5c'), {'ls_integration': 'deepagents', 'versions': {'deepagents': '0.5.3'}, 'lc_agent_name': None, 'langgraph_step': 4, 'langgraph_node': 'tools', 'langgraph_triggers': ('__pregel_push',), 'langgraph_path': ('__pregel_push', 0, False), 'langgraph_checkpoint_ns': 'tools:42e8be0a-0b64-d3a7-69c7-8501c5810dff'})
(AIMessageChunk(content='\n', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019dd76f-3b74-7492-bf5b-506b4c52884f', tool_calls=[], invalid_tool_calls=[], tool_call_chunks=[]), {'ls_integration': 'langchain_chat_model', 'versions': {'deepagents': '0.5.3'}, 'lc_agent_name': None, 'langgraph_step': 5, 'langgraph_node': 'model', 'langgraph_triggers': ('branch:to:model',), 'langgraph_path': ('__pregel_pull', 'model'), 'langgraph_checkpoint_ns': 'model:dba1bfdc-f988-68b5-ccc1-85e87aef99a0', 'checkpoint_ns': 'model:dba1bfdc-f988-68b5-ccc1-85e87aef99a0', 'ls_provider': 'openai', 'ls_model_name': 'glm-4', 'ls_model_type': 'chat', 'ls_temperature': None})
(AIMessageChunk(content='沈阳', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019dd76f-3b74-7492-bf5b-506b4c52884f', tool_calls=[], invalid_tool_calls=[], tool_call_chunks=[]), {'ls_integration': 'langchain_chat_model', 'versions': {'deepagents': '0.5.3'}, 'lc_agent_name': None, 'langgraph_step': 5, 'langgraph_node': 'model', 'langgraph_triggers': ('branch:to:model',), 'langgraph_path': ('__pregel_pull', 'model'), 'langgraph_checkpoint_ns': 'model:dba1bfdc-f988-68b5-ccc1-85e87aef99a0', 'checkpoint_ns': 'model:dba1bfdc-f988-68b5-ccc1-85e87aef99a0', 'ls_provider': 'openai', 'ls_model_name': 'glm-4', 'ls_model_type': 'chat', 'ls_temperature': None})'''


