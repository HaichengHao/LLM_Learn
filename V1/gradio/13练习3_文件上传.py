# @Time    : 2026/4/8 13:50
# @Author  : hero
# @File    : 13练习3_文件上传.py
import gradio as gr
import pathlib
suffix_allowed=['.jpg','.png','.txt','.bmp','.jpeg','.docx']
def get_file(f):
    print(pathlib.Path(f).name) #tips:打印文件名
    print(pathlib.Path(f).suffix)#tips:打印文件扩展名

    file_suffix=pathlib.Path(f).suffix
    if file_suffix in suffix_allowed:

        return f.split('/')[-1]+'上传成功🎉'
    else:
        # raise TypeError("格式不支持")
        return f"不允许上传,支持的格式有{suffix_allowed}"
with gr.Blocks() as main:
    file_upload=gr.File(
        label=f"上传文件,允许的格式有{suffix_allowed}"
    )
    #创建一个文本框，用于显示上传结果
    out_put = gr.Textbox(
        label="上传状态"
    )

    file_upload.upload(
        fn=get_file,
        inputs=file_upload,
        outputs=out_put
    )

if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8080,

    )