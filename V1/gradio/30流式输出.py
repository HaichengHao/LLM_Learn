# @Time    : 2026/4/9 10:15
# @Author  : hero
# @File    : 30流式输出.py
import random
import time

import gradio as gr



def do_it(message,history):
    res = ["hello",'xixi','算了','《呼啸山庄》是英国19世纪著名诗人和小说家艾米莉·勃朗特所创作的唯一的一部小说。作品出版于1847年,1984年江苏人民出版社出版了杨苡的中译本。小说叙述了一个复仇的故事:男主人公希刺克利夫是个被恩肖收养的弃儿。恩肖的儿子辛德力视他为奴仆,恩肖的女儿加瑟琳却与他相爱。后加瑟琳出于无奈嫁与阔少林顿,死于难产。希刺克利夫愤然出走。几年后归来已十分富有。为了对恩肖和林顿两家进行报复,他娶了林顿的妹妹伊萨贝拉,肆意虐待她,甚至虐待伊萨贝拉为他生的儿子。他还不惜加害于加瑟琳遗留的女儿小卡瑟,强迫病危的儿子和小卡瑟结婚。儿子死后,他独霸了恩肖和林顿两家的财产。在完全达到复仇的目的后,他便失去了生活的意义。小说最后,主人公在寂莫与空虚中悄然死去。埋葬在加瑟琳的墓旁。以残酷手段进行报复导致的这场悲剧,深刻地揭示出私有制社会固有的内在矛盾,而个人的消极反抗则最终遭到失败。']
    resp = random.choice(res)
    #流式输出
    letter=''
    for c in resp:
        letter+=c
        time.sleep(0.1)
        yield letter


interface = gr.ChatInterface(
    fn=do_it,
    autofocus=True,  # tips:实现每次对话完毕之后光标默认回到对话框内
    title="对话机器人框架原型",
    examples=['什么是Gradio', 'Langchain于llmindex的区别'],
    submit_btn='发送'
)

if __name__ == '__main__':

    interface.launch(
        server_name='localhost',
        server_port=8888
    )