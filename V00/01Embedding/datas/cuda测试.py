# @Time    : 2026/3/15 21:21
# @Author  : hero
# @File    : cuda测试.py

import torch

print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))