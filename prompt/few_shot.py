from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("MINIMAX_API_KEY"), base_url=os.getenv("MINIMAX_BASE_URL"))
model = os.getenv("MINIMAX_MODEL_CODE")

prompt = """
1. 生成文本：ChatGPT可以生成与给定主题相关的文章、新闻、博客、推文等等。您可以提供一些关键词或主题，然后ChatGPT将为您生成相关的文本。
2. 语言翻译：ChatGPT可以将一种语言的文本翻译成另一种语言。
3. 问答系统：ChatGPT可以回答您提出的问题，无论是事实性的问题、主观性的问题还是开放性的问题。
4. 对话系统：ChatGPT可以进行对话，您可以与ChatGPT聊天，让它回答您的问题或就某个话题进行讨论。
5. 摘要生成：ChatGPT可以从较长的文本中生成摘要，帮助您快速了解文章的主要内容。
6. 文本分类：ChatGPT可以将一些给定的文本分类到不同的类别中，例如新闻、体育、科技等等。
7. 文本纠错：ChatGPT可以自动纠正文本中的拼写错误和语法错误，提高文本的准确性。

请把上面7段话各自的开头几个词，翻译成英文，并按序号输出。例如，第1段话的开头是"生成文本"，那么就输出"generate text"
"""

# prompt = """
# "whatpu"是坦桑尼亚的一种小型毛茸茸的动物。一个使用whatpu这个词的句子的例子是：
# 我们在非洲旅行时看到了这些非常可爱的whatpus。
# "farduddle"是指快速跳上跳下。一个使用farduddle这个词的句子的例子是：
# """

# prompt = """
# 示例1：
# 输入："这个餐厅太棒了！" → 输出："正面"
# 示例2：
# 输入："等待时间过长，体验差。" → 输出："负面"
# ---
# 新输入："产品还行，但包装不好。"
# 输出：？
# """


def get_completion(prompt, model=model):
     messages = [{"role": "user", "content": prompt}]
     response = client.chat.completions.create(
         model=model,
         messages=messages,
         temperature=0, # 模型输出的随机性，0 表示随机性最小
     )
     return response.choices[0].message.content


print(get_completion(prompt))