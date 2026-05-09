# @Time    : 2026/5/7 20:45
# @Author  : hero
# @File    : 04续编解码.py

from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained('~/.cache/huggingface/hub/')

#tips:编码
'''
编码是将 tokenize + convert_tokens_to_ids 合并后的结果，通常还会自动添加特殊符号（如 [CLS] 和 [SEP]），除此之外，还支持padding、truncate等功能。'''
ids = tokenizer.encode("我爱自然语言处理")

print(ids)


#tips: 解码会将一个 token ID 序列还原为对应的原始文本（或接近的文本）

demo_ids = [101, 2769, 4263, 5632, 4197, 6427, 6241, 1905, 4415, 102]

string = tokenizer.decode(demo_ids,skip_special_tokens=True)

print(string)
# [CLS] 我 爱 自 然 语 言 处 理 [SEP]

#important: 注：可通过skip_special_tokens=True参数跳过特殊符号
