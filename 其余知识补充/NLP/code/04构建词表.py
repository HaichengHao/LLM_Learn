# @Time    : 2026/4/25 18:31
# @Author  : hero
# @File    : 04构建词表.py

import jieba

text = '天空好像下雨,我好想住你隔壁'

word_lst = jieba.lcut(text)

word2id={
    id:word for id,word in enumerate(word_lst)
}
print(word2id)

id2word={
    word:id for id,word in enumerate(word_lst)
}
print(id2word)
'''
Building prefix dict from the default dictionary ...
Loading model from cache /tmp/jieba.cache
{0: '天空', 1: '好像', 2: '下雨', 3: ',', 4: '我', 5: '好', 6: '想', 7: '住', 8: '你', 9: '隔壁'}
{'天空': 0, '好像': 1, '下雨': 2, ',': 3, '我': 4, '好': 5, '想': 6, '住': 7, '你': 8, '隔壁': 9}
Loading model cost 0.401 seconds.
Prefix dict has been built successfully.'''