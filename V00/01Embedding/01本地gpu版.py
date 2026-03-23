# @Time    : 2026/3/15 21:18
# @Author  : hero
# @File    : 01本地gpu版.py
# @Time    : 2026/3/15 18:15
# @Author  : hero (Modified for Local GPU)
# @File    : 01创建embedding模型_本地GPU版.py

import pandas as pd
import os
# 👇👇👇 关键步骤：设置国内镜像源 (必须在 import sentence_transformers 之前设置)
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
from sentence_transformers import SentenceTransformer
import torch

# ================= 配置区域 =================
# 1. 选择模型
# all-MiniLM-L6-v2: 速度快，显存占用小，适合大多数语义搜索任务 (推荐 RTX 2080 Ti)
# paraphrase-MiniLM-L6-v2: 类似，针对短语优化
# bge-large-zh-v1.5: 如果你主要处理中文，选这个 (但你的数据是英文评论，所以用上面的)
MODEL_NAME = "all-MiniLM-L6-v2"

# 2. 批处理大小 (Batch Size)
# RTX 2080 Ti (11GB) 处理短文本可以设大一点，加快推理速度
BATCH_SIZE = 128

# 3. 数据路径
DATA_PATH = './datas/fine_food_reviews_1k.csv'
# ===========================================

print(f"🚀 正在检查 GPU 环境...")
if not torch.cuda.is_available():
    print("❌ 警告：未检测到 CUDA！将使用 CPU 运行，速度会较慢。请检查 uv add 是否正确安装了 cu128 版本的 torch。")
    device = "cpu"
else:
    device = "cuda"
    print(f"✅ GPU 就绪：{torch.cuda.get_device_name(0)}")

# Step 1: 读取数据
print("📂 正在读取数据...")
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"找不到文件：{DATA_PATH}，请确认路径是否正确。")

df = pd.read_csv(DATA_PATH)

# 数据清洗 (保留原逻辑)
# 注意：原代码 df = df[df.columns[1:]] 是为了丢弃第一列（通常是索引列），这里保留
if df.columns[0] == 'Unnamed: 0' or df.columns[0].isdigit():
    df = df.iloc[:, 1:] # 更安全的丢弃第一列方式

df = df.dropna(subset=['Summary', 'Text']) # 确保 Summary 和 Text 不为空

# 构建组合文本
df['combined'] = "Title: " + df['Summary'].str.strip() + "; Content: " + df['Text'].str.strip()

# 排序并选取最新数据 (保留原逻辑)
if 'Time' in df.columns:
    df = df.sort_values('Time')
    df = df.tail(1000) # 取最近 1000 条
    df = df.drop(columns=['Time'])
else:
    print("⚠️ 未找到 'Time' 列，跳过时间排序，直接处理所有数据。")
    df = df.tail(1000)

print(f"📝 待处理数据量：{len(df)} 条")

# Step 2: 加载本地模型
print(f"🤖 正在加载模型：{MODEL_NAME} (首次运行会自动下载，请耐心等待...)")
# device='cuda' 强制使用显卡
model = SentenceTransformer(MODEL_NAME, device=device)

# Step 3: 生成 Embedding (核心改造部分)
print(f"⚡ 开始批量生成 Embedding (Batch Size={BATCH_SIZE}, Device={device})...")

texts = df['combined'].tolist()

# 使用 model.encode 进行批量推理
# convert_to_numpy=True: 返回 numpy 数组，方便存入 DataFrame
# show_progress_bar=True: 显示进度条
embeddings = model.encode(
    texts,
    batch_size=BATCH_SIZE,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=False # 如果需要计算余弦相似度，建议设为 True；若后续用 FAISS 等库，它们内部通常会处理或要求归一化
)

# 将结果存回 DataFrame
# embeddings 是一个 (N, D) 的 numpy 数组，直接赋值给一列即可
df['embedding'] = list(embeddings)

print("✅ 完成！")
print(f"💾 数据形状：{df.shape}")
print(f"🔢 向量维度：{len(df['embedding'].iloc[0])}")

# 预览结果
print("\n--- 前 3 条数据预览 ---")
print(df[['combined', 'embedding']].head(3))

# (可选) 保存结果到 CSV (注意：CSV 存储向量效率低，大项目建议存 parquet 或 pickle)
df.to_pickle("./datas/embeddings_local.pkl")
df.to_csv("./datas/embeddings_local.csv")
print("💾 已保存为 pickle 文件 (推荐格式)")
print("已保存为csv文件")