# @Time    : 2026/3/25 15:04
# @Author  : hero
# @File    : 11外部加载提示词.py

#important:注意,自定义的json和yaml开头的_type别乱写,就照着这样写
from langchain_core.prompts import load_prompt

template1 = load_prompt("./localprompttemplates/prompt.json",encoding='utf-8')

print(template1.format(name="张三",what="阿拉丁神灯"))


template2=load_prompt("./localprompttemplates/demoprompt.yaml",encoding='utf-8')
print(template2.format(name="李四",what="小红帽"))

'''
请张三讲一个阿拉丁神灯的故事
请李四讲一个小红帽的故事
'''