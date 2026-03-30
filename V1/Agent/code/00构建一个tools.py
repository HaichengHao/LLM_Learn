# @Time    : 2026/3/30 11:01
# @Author  : hero
# @File    : 00构建一个tools.py
from langchain_core.tools import tool

#theway 1通过装饰器的方式去定义一个

@tool
def calc_expo(base:int,exponent:int)->int:
    #tips:需要添加函数说明
    """
    指数计算
    :param base:
    :param exponent:
    :return: base**exponent
    """
    return base**exponent

print(calc_expo)
'''
name='calc_expo' 
description='指数计算\n:
param base:\n
:param exponent:\n
:return: base**exponent' 
args_schema=<class 'langchain_core.utils.pydantic.calc_expo'>
 func=<function calc_expo at 0x7a5804bceca0>'''
print(type(calc_expo))
# <class 'langchain_core.tools.structured.StructuredTool'>

#theway 2通过调用tool函数去定义
def calc_expo2(base:int,exponent:int)->int:
    #tips:需要添加函数说明
    """
    指数计算
    :param base:
    :param exponent:
    :return: base**exponent
    """
    return base**exponent

new_tool = tool(calc_expo2)
print(new_tool)
print(type(new_tool))
'''
<class 'langchain_core.tools.structured.StructuredTool'>
name='calc_expo2' d
escription='指数计算\n
:param base:\n
:param exponent:\n
:return: base**exponent' 
args_schema=<class 'langchain_core.utils.pydantic.calc_expo2'> 
func=<function calc_expo2 at 0x715ac52ac9a0>
<class 'langchain_core.tools.structured.StructuredTool'>
'''
#important:看看源码,tool返回的是一个BaseTool