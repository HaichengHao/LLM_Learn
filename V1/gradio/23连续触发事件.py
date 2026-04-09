# @Time    : 2026/4/8 16:59
# @Author  : hero
# @File    : 23连续触发事件.py
import gradio as gr


def plus1(i):
    return i + 1


def minus1(i):
    return i - 1


def split1(i):
    return 1 if i > 0 else -1


with gr.Blocks() as main:
    n1 = gr.Number(label='n1')
    n2 = gr.Number(label='n2')
    n3 = gr.Number(label='n3')
    n4 = gr.Number(label='n4')

    btn = gr.Button()
    # btn.click(
    #     plus1, n1, n2
    # ).then(minus1, n2, n3).then(split1, n3, n4)

    #important:更严谨,即自身不出错才继续传递
    btn.click(
        plus1, n1, n2
    ).success(minus1, n2, n3).success(split1, n3, n4)
if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8080,
    )
