# @Time    : 2026/4/8 17:16
# @Author  : hero
# @File    : 25examples.py
import gradio as gr
def add_book(book,books:list[str]):
    books.append(book)
    return books
with gr.Blocks() as main :
    books=gr.State([])
    # books=[]
    inp=gr.Textbox()
    outp=gr.Textbox()
    btn=gr.Button('添加图书')
    btn.click(
        add_book,
        inputs=[inp,books],
        outputs=outp
    )
    examples=gr.Examples(
        examples=[
            ["水浒传",["三国演义"]],
            ["红楼梦", ["三国演义","水浒传"]],
        ],
        inputs=[inp,books], #important:绑定组件
    )

if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8888,
    )