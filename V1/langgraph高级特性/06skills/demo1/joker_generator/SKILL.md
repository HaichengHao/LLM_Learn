---
name: joke-generator  
description: 
  当用户明确要求讲个笑话、需要幽默内容、想放松一下或类似请求时使用。
  此技能可以生成编程笑话、动物笑话或通用笑话。    
scripts: scripts/generate_joke.py    
---
## 执行步骤
.  **确定笑话类型**：根据用户请求判断笑话类型。如果没有指定，则默认为 `general`。    
    -   编程笑话 (`programming`)  
    -   动物笑话 (`animal`)  
    -   通用笑话 (`general`)  
.  **调用脚本**：运行 `scripts/generate_joke.py` 脚本，并通过 `--type` 参数传入上述类型。  
.  **返回结果**：脚本会输出一个 JSON 对象，例如 `{"joke": "内容"}`。将其中的 `joke` 字段内容直接呈现给用户。   

## 调用示例
```bash
# 生成一个编程笑话
python scripts/generate_joke.py --type programming

# 生成一个通用笑话（默认）
python scripts/generate_joke.py
```