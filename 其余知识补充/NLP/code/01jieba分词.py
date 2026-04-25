# @Time    : 2026/4/25 17:34
# @Author  : hero
# @File    : jieba分词.py

import jieba
demo_text='傻站在你家楼下抬起头数乌云'

#返回一个生成器
word_generator=jieba.cut(demo_text,cut_all=True) #tips:全模式分词可使用jieba.cut或者jieba.lcut，并将cut_all参数设置为True
for word in word_generator:
    print(word)


#返回一个列表
word_lst = jieba.lcut(demo_text)
print(word_lst)
'''
/home/nikofox/LLMlearn/其余知识补充/NLP/jieba分词.py 
Building prefix dict from the default dictionary ...
Loading model from cache /tmp/jieba.cache
Loading model cost 0.373 seconds.
Prefix dict has been built successfully.
傻站
在
你家
楼下
抬起
头数
乌云
['傻站', '在', '你家', '楼下', '抬起', '头数', '乌云']
'''