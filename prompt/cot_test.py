from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("MINIMAX_API_KEY"), base_url=os.getenv("MINIMAX_BASE_URL"))
model = os.getenv("MINIMAX_MODEL_CODE")

sudoku_puzzle = "3,*,*,2|1,*,3,*|*,1,*,3|4,*,*,1"
prompt = f"""
{sudoku_puzzle}
- 这是一个4x4数独谜题。
- * 代表待填充的单元格。
- | 字符分隔行。
- 在每一步中，用数字1-4替换一个或多个 *。
- 任何行、列或2x2子网格中都不能有重复的数字。
- 保留先前有效思维中已知的数字。
- 每个思维可以是部分或最终解决方案。
""".strip()

messages = [{"role": "user", "content": prompt}]

res = client.chat.completions.create(model=model, messages=messages)
for choice in res.choices:
    print(choice.message.content)