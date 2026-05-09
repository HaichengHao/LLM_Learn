# @Time    : 2026/5/7 16:28
# @Author  : hero
# @File    : 02小案例.py

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()
URI = "neo4j://localhost:7687"
AUTH = ("neo4j", os.getenv('neo4j_pwd'))

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print('connected is established')


    #查询某个导演在某个年份之后拍过的电影

    records,summary,keys=driver.execute_query(
        """
        MATCH (p:Person{name:$name})-[r:DIRECTED]->(m:Movie)
        WHERE m.year>$year
        RETURN p.name AS 导演 ,m.year AS 上映年份 ,m.title AS 电影名称
        """,
        parameters_={
            "name":"张艺谋",
            "year":1990 #tips:注意写为数字形式,别写字符串,不然where做比较运算时候会失效
        }
    )


    #tips:打印查询结果
    print(f"查询返回了{len(records)}记录\n运行时间{summary.result_available_after}\n查询到的匹配数据如下:\n")
    for record in records:
        print(record.data())
    for record in records: #tips:或者我们按照它原始的形式,records返回的是一个列表里边包含字典,我们就用取值法输出自定义字符串
        print(f'{record["导演"]}在{record["上映年份"]}导演了{record["电影名称"]}')
    '''
    connected is established
    查询返回了3记录
    运行时间0
    查询到的匹配数据如下:
    
    {'导演': '张艺谋', '上映年份': 2023, '电影名称': '满江红'}
    {'导演': '张艺谋', '上映年份': 2002, '电影名称': '英雄'}
    {'导演': '张艺谋', '上映年份': 1994, '电影名称': '活着'}
    张艺谋在2023导演了满江红
    张艺谋在2002导演了英雄
    张艺谋在1994导演了活着
    '''