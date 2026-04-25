# @Time    : 2026/4/25 17:41
# @Author  : hero
# @File    : jieba搜索引擎模式.py

'''
在精确模式基础上，对长词进一步切分，适合用于搜索引擎分词，
可使用jieba.cut_for_search或者jieba.lcut_for_search，具体代码如下：
'''
import jieba

text="为你唱这首歌没有什么风格，它仅仅代表着我希望你快乐"

word_generator = jieba.cut_for_search(text)
for word in word_generator:
    print(word)

word_lst = jieba.lcut_for_search(text)
print(word_lst)

'''
Building prefix dict from the default dictionary ...
Loading model from cache /tmp/jieba.cache
为
你
唱
这
首歌
没有
什么
风格
，
它
仅仅
代表
着
我
希望
你
快乐
['为', '你', '唱', '这', '首歌', '没有', '什么', '风格', '，', '它', '仅仅', '代表', '着', '我', '希望', '你', '快乐']
Loading model cost 0.381 seconds.
Prefix dict has been built successfully.'''