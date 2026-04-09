# @Time    : 2026/4/8 21:23
# @Author  : hero
# @File    : 29进度条.py
import time

import gradio as gr



def do_it(input_word:str,progress=gr.Progress()):
    res = ""
    progress(progress=0,desc="开始....")
    #进度条滚动,输出一个字符往前移动
    for letter in progress.tqdm(input_word,desc="运行中..."):
        time.sleep(0.25)
        res += letter

    return res

interface = gr.Interface(
    fn=do_it,
    inputs=[
        gr.Textbox('输入任何文本')

    ],
    outputs="text"
)

if __name__ == '__main__':

    interface.launch(
        server_name='localhost',
        server_port=8888
    )