# @Time    : 2026/4/10 18:04
# @Author  : hero
# @File    : 12自定义reducer.py

'''
为了解决数值相乘的问题,需要我们自定义reducer了
'''

from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated


#important：自定义reducer

def CustomReducer(current:float,update:float)->float:
    '''
    自定义reducer,处理初始值，从0.0掰到1.0
    实现如果是第一次调用,current默认值为1.0
    :param current:
    :param update:
    :return:
    '''

    if current == 0.0:
        #对于乘法，恒等元应该是1.0或者return 1.0*update
        print(f'current is {current}')
        print(f'update is {update}')
        return 1.0*update
    else:
        return current*update #tips:这样就避免了首次相乘中langgraph自动将恒等元作为0.0的情况了


#定义state_schema

class MultiplyState(StateGraph):
    factor:Annotated[float,CustomReducer] #tips:这里不用reducer函数了,传我们自己的函数!


def multiplier(state:MultiplyState):
    return {
        'factor':2.0
    }

def multiplier2(state:MultiplyState):
    return {
        'factor':3.0
    }


def main():
    builder = StateGraph(MultiplyState)
    builder.add_node('m1',multiplier)
    builder.add_node('m2',multiplier2)
    builder.add_edge(START,'m1')
    builder.add_edge(START,'m2')
    builder.add_edge('m1',END)
    builder.add_edge('m2',END)

    app = builder.compile()
    return app

if __name__ == '__main__':
    app = main()
    res = app.invoke(
        {'factor':2.0},
    )

    print(res)
    print(app.get_graph().print_ascii())

'''
current is 0.0
update is 2.0
{'factor': 12.0}  成功,进行了自定义的reducer之后,将恒等元修改为了1*而不是0*，这样1*传入的update,也就是factor的值就是正常的开始做乘法了
  +-----------+    
  | __start__ |    
  +-----------+    
      *     *      
     *       *     
    *         *    
+----+      +----+ 
| m1 |      | m2 | 
+----+      +----+ 
      *     *      
       *   *       
        * *        
    +---------+    
    | __end__ |    
    +---------+    
None

Process finished with exit code 0


'''