# @Time    : 2026/3/21 19:59
# @Author  : hero
# @File    : demo4.py

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
base_url = os.getenv('base_url')
api_key=os.getenv("api_key")
client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

completion = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {"role":"system","content":"你是一个伟大的悬疑小说家"},
        {"role":"user","content":"帮我生成一个200字左右的悬疑小说,简短又能引起遐想,没必要有结局"}
    ]
)
print(completion)
"""
/home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/V0/openai/demo4.py 
ChatCompletion(id='chatcmpl-DLpb9DWFVbHVxDI9tqnW4ocaI6Psj', 
choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='在一个阴雨绵绵的下午，
小镇的图书馆里，年轻的图书管理员艾莉发现了一本封面破旧的日记，书页泛黄，字迹模糊。她翻开第一页，看到一行字写着：“此地有不速之客。”艾莉心中一紧，
好奇心驱使她继续阅读。日记的主人似乎是在描述一些诡异的事件：午夜时分，图书馆里时常会听到低语声，书架间古怪的影子，以及一个غط着面纱的陌生人。
\n\n她决定在晚上留守图书馆，想要查明真相。夜深人静时，艾莉隐约听见低沉的呢喃声，心跳加速。她朝着声音来源走去，突然发现书架上有一本与日记相同的封面。
仿佛她被无形的力量吸引，手指轻轻触碰它的边缘，霎时间，冷风刮过，图书馆的灯光闪烁不定，周围的书籍如同活物般颤动。\n\n就在这时，一个虚幻的身影从书架
后面闪出，面纱下的眼睛直勾勾盯着她。艾莉感觉到一股不祥的预感，她不知道自己已经被卷入了一个深不可测的秘密之中。', refusal=None, role='assistan
t', annotations=[], audio=None, function_call=None, tool_calls=None), content_filter_results={'hate': {'filtered': False
, 'severity': 'safe'}, 'protected_material_code': {'detected': False, 'filtered': False}, 'protected_material_text': 
{'detected': False, 'filtered': False}, 'self_harm': {'filtered': False, 'severity': 'safe'}, 'sexual': {'filtered': 
False, 'severity': 'safe'}, 'violence': {'filtered': False, 'severity': 'safe'}})], created=1774095603, 
model='gpt-4o-mini-2024-07-18', object='chat.completion', service_tier=None, system_fingerprint='fp_eb37e061ec', 
usage=CompletionUsage(completion_tokens=323, prompt_tokens=49, total_tokens=372, 
completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, 
rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0)), 
prompt_filter_results=[{'prompt_index': 0, 'content_filter_results': {'hate': {'filtered': False, 'severity': 'safe'}, 
'jailbreak': {'detected': False, 'filtered': False}, 'self_harm': {'filtered': False, 'severity': 'safe'}, 'sexual':
 {'filtered': False, 'severity': 'safe'}, 'violence': {'filtered': False, 'severity': 'safe'}}}])
"""
print(completion.choices[0].message)