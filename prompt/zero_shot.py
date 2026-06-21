from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("MINIMAX_API_KEY"),
                base_url=os.getenv("MINIMAX_BASE_URL"))
model = os.getenv("MINIMAX_MODEL_CODE")

# 情感分析
prompt = """
将文本分类为中性、负面或正面。
文本：我认为这家餐馆的菜品非常好吃。
情感：
"""

# 在上面的提示中，我们没有向模型提供任何示例——这就是零样本能力的作用。

def get_completion(prompt, model=model):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
    )
    return response.choices[0].message.content

print(get_completion(prompt))