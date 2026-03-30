# @Time    : 2026/3/30 11:14
# @Author  : hero
# @File    : 01tool的调用.py

from langchain_core.tools import tool

@tool
def calc_expo(base:int, exponent:int):
    """
    返回计算后的指数
    :param base:
    :param exponent:
    :return:
    """
    return base**exponent


#tips:调用
#important:注意，由于它不再是普通的函数，所以调用的时候要使用invoke调用,tool本身也继承了Runnable所以可以用invoke调用

res = calc_expo.invoke({
    'base':2,
    'exponent':3
})

print(res)
# 8 成功!!