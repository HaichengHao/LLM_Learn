# @Time    : 2026/4/16 10:05
# @Author  : hero
# @File    : 03PSQLPersistence.py
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph,START,END
import psycopg
from typing import TypedDict,Annotated
import operator

class DemoState(TypedDict):
    demostr:Annotated[list[str],operator.add]

def node_1(state:DemoState):
    return {
        'demostr':['12581','qevbe']
    }

def main():
    conn=psycopg.connect(
        dbname="llmdb",
        autocommit=True
    )

    psqlDB=PostgresSaver(conn=conn)
    psqlDB.setup()#important: 首次运行时创建 checkpoint 表


    graph = (
        StateGraph(DemoState)
        .add_node('node_1',node_1)
        .add_edge(START,'node_1')
        .add_edge('node_1',END)

        .compile(checkpointer=psqlDB)
    )

    config=RunnableConfig(
        configurable={
            'thread_id':'user-001'
        }
    )

    initial_state=graph.get_state(config)

    print(f'Initial state{initial_state}')


    print('='*10+'执行图'+'='*10+'\n')
    result=graph.invoke({'demostr':[]},config)
    print(f'result: {result}')
    print()
    final_state=graph.get_state(config)
    print(f'Final state{final_state}')

    conn.close()

if __name__ == '__main__':
    main()

'''
Final stateStateSnapshot(values={'demostr': ['12581', 'qevbe', '12581', 'qevbe']}

两次运行后的结果!!!!可以看到数据库中确实有旧的值和新的值!!!
'''