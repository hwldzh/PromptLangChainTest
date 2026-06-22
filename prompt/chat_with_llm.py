from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("MINIMAX_API_KEY"), base_url=os.getenv("MINIMAX_BASE_URL"))
model = os.getenv("MINIMAX_MODEL_CODE")
# 初始化系统消息
system_message = {
    'role': 'system',
    'content': '我是你的助手，我的名字叫tom，我能够帮助您解决各种各样的问题！'
}

# 存储对话历史
messages = [system_message]

# 开始多轮对话
while True:
    user_prompt = input('请输入你的问题（输入"退出"结束对话）：')

    # 检查是否退出对话
    if user_prompt.lower() == '退出':
        print("对话结束，感谢使用。")
        break

    # 添加用户消息到对话历史
    messages.append({'role': 'user', 'content': user_prompt})

    # 向模型发送消息并获取回复
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    # 打印模型的回复
    assistant_reply = response.choices[0].message.content
    print(assistant_reply)

    # 添加助手回复到对话历史
    messages.append({'role': 'assistant', 'content': assistant_reply})