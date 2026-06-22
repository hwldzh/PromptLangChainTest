from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # 从我们的env文件中加载出对应的环境变量

client = OpenAI(api_key=os.getenv("MINIMAX_API_KEY"), base_url=os.getenv("MINIMAX_BASE_URL"))
model = os.getenv("MINIMAX_MODEL_CODE")
user_prompt = "写一个3句话的睡前故事，主角是一只小猫，风格温馨有趣。"
response = client.chat.completions.create(
    model=model,
    messages=[
        {
            'role': 'system',
            'content': '我是你的助手，我的名字叫tom，我能够帮助您解决各种各样的问题！'
        },
        {
            'role': 'user',
            'content': user_prompt
        }
    ],
    # 0.1-0.6之间，回复会更贴切与实际情况，0.6-0.9之间，中间值，大于1，回复的内容更具有随机性
    temperature=0.1
)

print(response.choices[0].message.content)