# @Time    : 2026/5/7 12:06
# @Author  : hero
# @File    : 01python连接neo4j.py
'''
需要uv add neo4j
'''
# tips: https://neo4j.com/docs/python-manual/current/query-simple/ 官网文档
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

password = os.getenv('neo4j_pwd')

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", password)
# 通过创建 Driver 对象并提供 URL 和身份验证令牌来连接到数据库
# 获取 Driver 实例后，使用 .verify_connectivity() 方法确保可以建立有效的连接
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connection established.")

    # 写入数据 C
    # summary=driver.execute_query(
    #     """
    #     CREATE (u1:User{name:$name})""",
    #     name='Niko'
    # ).summary
    # print(summary)
    # print(f'成功创建节点{summary.counters.nodes_created},耗时{summary.result_available_after}')
    #

    # 写入数据,以字典传入参数
    # params={
    #     'name':'minko',
    #     'age':18
    # }
    # summary = driver.execute_query(
    #     """
    #     MERGE (:User{name:$name,age:$age})""",
    #     params
    # ).summary



    #================================================================
    # 查询数据 R
    '''
    	1.records 返回包含查询结果的记录列表,每条记录是一个字典对象,如果只是单纯create的话就没有返回查询结果，
    	自然上面的创建操作就不需要接收这个返回值
        2.summary 执行摘要，包含命中数、耗时、是否更新等信息
        3.keys 返回结果的字段名列表
    '''
    # records, summary,keys = driver.execute_query(
    #     """
    #     MATCH (u:User{name:'Bob'})
    #     RETURN u.name AS name
    #     """
    #
    # )
    #

    #
    # print(f'查询{summary.query}返回的记录长度为{len(records)},耗费时间为{summary.result_available_after}')
    '''
    Connection established.
    {'name': 'Bob'}
    查询
            MATCH (u:User{name:'Bob'})
            RETURN u.name AS name
            返回的记录长度为1,耗费时间为1
    '''

    # ================================================================
    #更新 U
    # records,summary,keys=driver.execute_query(
    #     """
    #     MATCH(u:User{name:'Bob'})
    #     SET u:Person ,u.hobby='dance'
    #     """
    # )
    # print(f'更新{summary.counters}\n执行{summary.query}')

    '''
    更新SummaryCounters{properties_set: 1, contains_updates: True, contains_system_updates: False}
    执行
            MATCH(u:User{name:'Bob'})
            SET u:Person ,u.hobby='dance'
    '''
    # ================================================================

    #删除 D

    records,summary,keys = driver.execute_query(
        """
        MATCH(p:User {name:'minko')  
        DETACH DELETE p
        """
    )

    print(f'{summary.counters}')

