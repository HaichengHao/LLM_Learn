# @Time    : 2026/4/14 11:12
# @Author  : hero
# @File    : 26api_send.py


#important：send和之前的区别就是send是分发，万箭齐发,而不是条件边那样匹配一条边走到底
# send要解决的是一个节点向其它多个节点分发状态，匹配多个路由的场景,如一个任务下达给多个智能体协同
'''
默认情况下，Nodes 和 Edges 是预先定义的，并对相同的共享状态进行操作。但是，在某些情况下，确切的边可能无法预先知道，
或者你可能希望同时存在不同版本的 State。一个常见的例子是 map-reduce 设计模式。在此设计模式中，第一个节点可能生成一个对象列表，
你可能希望将其他某个节点应用于所有这些对象。对象的数量可能无法预先知道（意味着边的数量可能无法知道），并且下游 Node 的输入 State 应该不同（每个生成的对象一个）。

为了支持这种设计模式，LangGraph 支持从条件边返回 Send 对象。
Send 接受两个参数：
       第一个是节点的名称，
       第二个是要传递给该节点的状态。

def continue_to_jokes(state: OverallState): #important:注意,返回的是一个列表,列表内的元素是一个个Send()对象
    return [Send("generate_joke"(目标转送节点名称), {"subject": s}(返回给节点的状态state)) for s in state['subjects']] #tips:也就是将任务发送到一个节点并传入状态

graph.add_conditional_edges("node_a", continue_to_jokes)

简单理解就是动态的创建多个执行分支,实行并行处理,每个send对象都指定了一个执行目标节点和传递给该节点的参数
langgraph会并行执行所有的这些任务,常用在Map-Reduce的场景,并行执行多个子节点并最终汇总到一个总节点

多路并进,汇总规约


也就是说，以前做条件边，整体走的还是一条一条来，但是现在是一起上，是分发，而不是匹配规则后转发!!!

Send的两个参数是十分重要的,一个是节点名称,一个是节点状态


整体步骤

1.route_tasks函数返回List[Send],每个Send都会触发一个独立的process_task节点并行执行，各自携带自己的私有状态
2.graph.add_conditional_edges("genetate_tasks", route_tasks)上游的generate_tasks执行完,调用路由函数生成
所有的Send指令,完成任务分发
3.graph.add_edge('process_task','reduce_results'):将所有process_task执行完毕,才执行汇总节点reduce_results
'''


import uuid
from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
from langgraph.types import Send

class DemoState(TypedDict):
    subjects:list[str]
    jokes:Annotated[list[str],lambda x,y:x+y]

#定义第一个节点函数,生成需要处理的主题列表
def generate_subjects(state:DemoState):
    """生成需要处理的主题列表"""
    print("执行节点(第一个节点:生成需要处理的主题列表):generate_subjects")
    subjects=['猫','狗','程序员']
    print(f'生成主题列表:{subjects}')
    return {
        'subjects':subjects
    }

'''
这里返回的就是
 return {
        'subjects':['猫','狗','程序员']
    }
'''



#条件边函数:根据主题列表生成Send对象列表
def map_subjects_to_jokes(state:DemoState) ->list[Send]:
    """
    将主题列表映射到joke生成任务
    :param state:
    :return:
    """

    print('执行条件边函数:map_subjects_to_jokes')
    subjects = state['subjects']  #['猫','狗','程序员']

    print(f'映射主题到joke任务:{subjects}')

    #为每个主题创建一个Send对象,指向make_joke节点
    #每个Send对象包含节点名称和传递给该节点的状态
    #important:注意,构造是Send对象组成的列表
    send_list = [
        Send("make_joke",{'subject':subject}) for subject in subjects   #['猫','狗','程序员']
    ] #tips:这里就是构造了send_list=[Send('make_joke',{'subject':'猫'}),Send('make_joke',{'subject':'狗'}),Send('make_joke',{'subject':'程序员'})]
    print(f'生成Send对象列表:{send_list}')
    return send_list #[Send('make_joke',{'subject':'猫'}),Send('make_joke',{'subject':'狗'}),Send('make_joke',{'subject':'程序员'})] #important：全部分发给make_joke,表现上是并行的,其实本身是串行的


#Map节点:为每个主题生成笑话

def make_joke(state:DemoState):
    subject = state.get("subject","未知") #tips:获取subject,得不到默认就返回未知    [Send('make_joke',{'subject':'猫'}),Send('make_joke',{'subject':'狗'}),Send('make_joke',{'subject':'程序员'})]表现为多条并行,其实是一条条拿出
    print(f'执行节点:make_joke,处理主题:{subject}')

    #根据主题生成相应的笑话
    jokes_map={
        "猫": "为什么猫不喜欢在线购物？因为它们更喜欢实体店！",
        "狗": "为什么狗不喜欢计算机？因为它们害怕被鼠标咬！",
        "程序员": "为什么程序员喜欢洗衣服？因为他们在寻找bugs！",
        "未知": "这是一个关于未知主题的神秘笑话。"
    }

    joke = jokes_map.get(subject,f'这是一个关于{subject}的笑话')
    print(f'生成笑话{joke}')
    return {
        'jokes':[joke]
    }

def main():
    '''演示map-reduce模式'''
    print('===Map-Reduce模式演示===\n')

    #创建图
    builder = StateGraph(DemoState)

    #添加节点
    builder.add_node(
        'generate_subjects',
        generate_subjects
    )
    builder.add_node(
        'make_joke',
        make_joke
    )




    #添加边
    builder.add_edge(
        START,'generate_subjects',
    )
    #添加条件边,使用Send对象实现map-reduce
    builder.add_conditional_edges(
        'generate_subjects', #源节点
        map_subjects_to_jokes  #路由函数,返回Send对象列表
    )

    #从make_joke到结束
    builder.add_edge(
        'make_joke',
        END
    )

    #编译图
    graph = builder.compile()
    print(graph.get_graph().print_ascii())

    file_pth = '../demoimgs/send'+str(uuid.uuid4())[:8]+'.png'
    with open(file_pth,'wb') as f:
        f.write(
            graph.get_graph().draw_mermaid_png()
        )

    #执行图
    initial_state={
        'subjects':[],
        'jokes':[]
    }
    print('初始状态',initial_state)
    print('\n开始执行图')

    result = graph.invoke(initial_state)
    print(f'\n最终结果:{result}')

    print('\n===演示完成===')

if __name__ == '__main__':
    main()


'''
===Map-Reduce模式演示===

    +-----------+      
    | __start__ |      
    +-----------+      
          *            
          *            
          *            
+-------------------+  
| generate_subjects |  
+-------------------+  
          *            
          *            
          *            
     +---------+       
     | __end__ |       
     +---------+       
None
初始状态 {'subjects': [], 'jokes': []}

开始执行图
执行节点(第一个节点:生成需要处理的主题列表):generate_subjects
生成主题列表:['猫', '狗', '程序员']
执行条件边函数:map_subjects_to_jokes
映射主题到joke任务:['猫', '狗', '程序员']
生成Send对象列表:[Send(node='make_joke', arg={'subject': '猫'}), Send(node='make_joke', arg={'subject': '狗'}), Send(node='make_joke', arg={'subject': '程序员'})]
执行节点:make_joke,处理主题:猫
生成笑话为什么猫不喜欢在线购物？因为它们更喜欢实体店！
执行节点:make_joke,处理主题:狗
生成笑话为什么狗不喜欢计算机？因为它们害怕被鼠标咬！
执行节点:make_joke,处理主题:程序员
生成笑话为什么程序员喜欢洗衣服？因为他们在寻找bugs！

最终结果:{'subjects': ['猫', '狗', '程序员'], 'jokes': ['为什么猫不喜欢在线购物？因为它们更喜欢实体店！', '为什么狗不喜欢计算机？因为它们害怕被鼠标咬！', '为什么程序员喜欢洗衣服？因为他们在寻找bugs！']}

===演示完成===
'''

#important 一定要去看看mermaid图,因为会发现其实有一个节点是没有任何连接的