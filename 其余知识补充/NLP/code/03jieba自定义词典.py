# @Time    : 2026/4/25 17:44
# @Author  : hero
# @File    : 03jieba自定义词典.py

'''
jieba支持用户自定义词典，以便包含 jieba 词库里没有的词，用于增强特定领域词汇的识别能力。
自定义词典的格式为：一个词占一行，
每一行分三部分：词语、
词频（可省略，词频决定某个词在分词时的优先级。词频越高被优先切分出来的概率越大）、
词性标签（可省略，不影响分词结果），用空格隔开，顺序不可颠倒。


------
可使用jieba.load_userdict(file_name)加载词典文件，
也可以使用jieba.add_word(word, freq=None, tag=None)
与jieba.del_word(word)动态修改词典。
'''

import jieba
jieba.load_userdict('../assets/user_dict.txt')

text = "随着云计算技术的普及，越来越多企业开始采用云原生架构来部署服务，并借助大模型能力提升智能化水平，实现业务流程的自动化与智能决策。"
word_lst=jieba.lcut(text)
print(word_lst)
'''
Building prefix dict from the default dictionary ...
Loading model from cache /tmp/jieba.cache
['随着', '云计算', '技术', '的', '普及', '，', '越来越', '多', '企业', '开始', '采用', '云原生', '架构', '来', '部署', '服务', '，', '并', '借助', '大模型', '能力', '提升', '智能化', '水平', '，', '实现', '业务流程', '的', '自动化', '与', '智能', '决策', '。']
Loading model cost 0.380 seconds.
Prefix dict has been built successfully.
'''