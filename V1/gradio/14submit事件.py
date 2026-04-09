# @Time    : 2026/4/8 14:24
# @Author  : hero
# @File    : 14submit事件.py

import gradio as gr
def sayhi(name):
    return f"Hi {name}"

with gr.Blocks() as main:
    input = gr.Textbox(placeholder="输入你的名字")
    out_put =gr.Textbox(placeholder="测试输出")

    btn = gr.Button(
        value="点我提交或回车提交",

    )

    #tips:某些情况下不想非要点击按钮提交而是回车提交，那就像H5中学到的addEventlistener('onsubmit',function(){xxx})
    # h5中是给指定的表单加上该事件,而这里我们也是给input添加上提交事件
    input.submit(
        fn=sayhi,
        inputs=input,
        outputs=out_put
    )


if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8080,
    )