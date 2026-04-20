# @Time    : 2026/4/18 10:11
# @Author  : hero
# @File    : generate_joke.py
#!/usr/bin/env python3
import json
import random
import argparse

JOKES = {
    "programming": [
        "为什么程序员分不清万圣节和圣诞节？因为 Oct 31 == Dec 25！",
        "有一个 null 指针走进了酒吧... 然后它就崩溃了。",
    ],
    "animal": [
        "为什么鸡过马路？为了证明它不是懦夫！",
        "企鹅去银行存钱，柜员问：‘有账户吗？’ 企鹅说：‘没有，我是企鹅。’"
    ],
    "general": [
        "我昨天把手机扔进海里了——现在它变成了‘盐水机’。",
        "我妈说我小时候很聪明，直到我把遥控器放进微波炉‘充电’。"
    ]
}

def main():
    parser = argparse.ArgumentParser() #Object for parsing command line strings into Python objects.源码注释，也就是把命令行字符串转换为python对象
    parser.add_argument("--type", default="general", choices=["programming", "animal", "general"])
    args = parser.parse_args()

    joke = random.choice(JOKES[args.type])
    print(json.dumps({"joke": joke}, ensure_ascii=False))

if __name__ == "__main__":
    main()