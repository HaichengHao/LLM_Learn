# @Time    : 2026/5/7 18:20
# @Author  : hero
# @File    : 02AutoModelForXXX类.py
'''
AutoModel 只加载预训练模型的主干结构，不包含任何任务相关的输出层，适用于特征提取或自定义模型结构的场景。
除此之外，Transformers 还提供了用于具体任务的专用模型类：AutoModelForXXX，这些类在模型主干的基础上，
自动添加了适配任务的输出层（通常称为“任务头”或 Task Head），使模型能够直接用于分类、命名实体识别、问答等标准 NLP 任务的训练与推理，无需手动修改结构。


模型类名称	适用任务类型	简要说明
AutoModelForCausalLM	自回归语言建模	用于根据已有文本逐字生成后续文本
AutoModelForSeq2SeqLM	序列到序列生成任务	适用于机器翻译、文本摘要、对话生成
AutoModelForSequenceClassification	文本分类	例如情感分析、主题分类、多标签分类
AutoModelForTokenClassification	Token 级别标注任务	如命名实体识别（NER）
AutoModelForQuestionAnswering	抽取式问答	用于从上下文中找出答案的起始和结束位置
'''

from transformers import AutoModelForCausalLM, AutoModelForSequenceClassification, AutoModelForTokenClassification,\
    AutoModelForDocumentQuestionAnswering

# 上述AutoModelForXXX类的用法与AutoModel类一致，例如现在需要一个基于bert-base-chinese的文本分类模型，便可直接通过以下代码进行加载


model=AutoModelForTokenClassification.from_pretrained("google-bert/bert-base-chinese")
'''
上述代码得到的model的类型为BertForSequenceClassification。模型结构包括：
BERT 编码器主干；
一个线性层（任务头），用于输出每个类别的得分。
此外，对于特定任务的模型，我们还可以在 from_pretrained() 中设置一些参数用于控制任务头的行为，例如
'''

model2=AutoModelForSequenceClassification.from_pretrained(
    "google-bert/bert-base-chinese",
    num_labels=3,
)
'''
num_labels	指定分类任务的类别数，默认值为 2。用于构建分类头的输出维度
'''