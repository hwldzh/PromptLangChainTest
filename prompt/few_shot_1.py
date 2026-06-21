from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("MINIMAX_API_KEY"), base_url=os.getenv("MINIMAX_BASE_URL"))
model = os.getenv("MINIMAX_MODEL_CODE")

prompt = """
这组数字中的奇数加起来是一个偶数：4、8、9、15、12、2、1。
A：答案是False。

这组数字中的奇数加起来是一个偶数：17、10、19、4、8、12、24。
A：答案是True。

这组数字中的奇数加起来是一个偶数：16、11、14、4、8、13、24。
A：答案是True。

这组数字中的奇数加起来是一个偶数：17、9、10、12、13、4、2。
A：答案是False。

这组数字中的奇数加起来是一个偶数：15、32、5、13、82、7、1。
A：
"""

# usage
def get_completion(prompt, model=model):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
    )
    return response.choices[0].message.content

print(get_completion(prompt))