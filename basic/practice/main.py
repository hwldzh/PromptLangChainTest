
import asyncio
import json
import logging
from contextlib import asynccontextmanager
import re
import time
from typing import List, Optional
import uuid
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from pydantic import BaseModel, Field
import uvicorn
from langchain_openai import ChatOpenAI
# 部署REST API相关
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROMPT_TEMPLATE_TXT_SYS = "prompt_template_system.txt"
PROMPT_TEMPLATE_TXT_USER = "prompt_template_user.txt"

PORT = 8082
API_BASE_URL = "https://api.minimaxi.com/v1"
CHAT_API_KEY = "sk-cp-C7X-cFbQJWyglSTgShzc-KVNUmCR45j2V5G5urOihL94a8b9qiPLVF3VWcvDJWiLM68wg6AEAtXEHrL39bv5QnTNfEHRaQmDrQDEMpGwRwrxG0Vy0_MnAsQ"
CHAT_MODEL = "MiniMax-M2.7-highspeed"

# 声明全局变量，全局调用
model = None

app = FastAPI(lifespan=lifespan)

def getPrompt(prompt):
    logger.info(f"最后给到LLM的prompt内容为：{prompt}")
    return prompt


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    # 申明引用全局变量，在函数中被初始化，并在整个应用中使用
    global model, prompt, chain, API_TYPE, PROMPT_TEMPLATE_TXT_SYS, PROMPT_TEMPLATE_TXT_USER
    global ONEAPI_API_BASE, ONEAPI_CHAT_API_KEY, ONEAPI_CHAT_MODEL
    global OPENAI_API_BASE, OPENAI_CHAT_API_KEY, OPENAI_CHAT_MODEL
    try:
        logger.info("正在初始化大模型、提取prmopt、定义chain...")
        model = ChatOpenAI(base_url=API_BASE_URL, 
                api_key=CHAT_API_KEY, 
                model=CHAT_MODEL, temperature=0.4)
        prompt_template_system = PromptTemplate.from_file(PROMPT_TEMPLATE_TXT_SYS, encoding='utf-8')
        prompt_template_user = PromptTemplate.from_file(PROMPT_TEMPLATE_TXT_USER, encoding='utf-8')
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_template_system.template),
            ("human", prompt_template_user.template)
        ])
        chain = prompt | getPrompt | model
        logger.info(f"初始化完成，可以开始接收请求")
    except Exception as e:
        logger.error(f"初始化失败，请检查配置文件")
        # raise 关键字重新抛出异常，以确保程序不会在错误状态下继续运行
        raise
    yield
    logger.info("正在关闭应用...")

class Message(BaseModel):
    role: str
    content: str


class ChatCompleteRequest(BaseModel):
    messages: List[Message]
    stream: Optional[bool] = False

class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: Message
    finish_reason: Optional[str] = None

class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcompl-{uuid.uuid4().hex}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    choices: List[ChatCompletionResponseChoice]
    system_fingerprint: Optional[str] = None


# 格式化响应，对输入的文本进行段落分隔、添加适当的换行符，以及在代码块中增加标记，以便生成更具可读性的输出
def format_response(response):
    # 使用正则表达式 \n{2, }将输入的response按照两个或更多的连续换行符进行分割。这样可以将文本分割成多个段落，每个段落由连续的非空行组成
    paragraphs = re.split(r'\n{2,}', response)
    # 空列表，用于存储格式化后的段落
    formatted_paragraphs = []
    # 遍历每个段落进行处理
    for para in paragraphs:
        # 检查段落中是否包含代码块标记
        if '```' in para:
            # 将段落按照```分割成多个部分，代码块和普通文本交替出现
            parts = para.split('```')
            for i, part in enumerate(parts):
                # 检查当前部分的索引是否为奇数，奇数部分代表代码块
                if i % 2 == 1:  # 这是代码块
                    # 将代码块部分用换行符和```包围，并去除多余的空白字符
                    parts[i] = f"\n```\n{part.strip()}\n```\n"
            # 将分割后的部分重新组合成一个字符串
            para = ''.join(parts)
        else:
            # 否则，将句子中的句点后面的空格替换为换行符，以便句子之间有明确的分隔
            para = para.replace('. ', '.\n')
        # 将格式化后的段落添加到formatted_paragraphs列表
        # strip()方法用于移除字符串开头和结尾的空白字符（包括空格、制表符 \t、换行符 \n等）
        formatted_paragraphs.append(para.strip())
    # 将所有格式化后的段落用两个换行符连接起来，以形成一个具有清晰段落分隔的文本
    return '\n\n'.join(formatted_paragraphs)


async def chat_compltetions(request: ChatCompleteRequest):
    if not model or not prompt or not chain:
        logger.error("服务未初始化")
        raise HTTPException(status_code=500, detail="服务未初始化")
    try:
        logger.info(f"收到聊天完成请求: {request}")
        query_prompt = request.message[-1].content
        logger.info(f"用户问题是: {query_prompt}")

        result = chain.invoke(
            {"query": query_prompt}
        )

        formatted_response = str(format_response(result.content))
        logger.info(f"返回给用户的响应是: {formatted_response}")

        if request.stream:
            async def generate_stream():
                chunk_id = f"chatcompl-{uuid.uuid4().hex}"
                lines = formatted_response.split("\n")
                for i, line in enumerate(lines):
                    chunk = {
                        "id": chunk_id,
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"content": line + "\n"},
                                "finish_reason": None
                            }
                        ]
                    }
                    yield f"{json.dumps(chunk)}\n"
                    await asyncio.sleep(0.5)
                final_chunk = {
                    "id": chunk_id,
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "choices": [
                        {
                            "index": 0,
                            "delta": {},
                            "finish_reason": "stop"
                        }
                    ]
                }
                yield f"{json.dumps(final_chunk)}\n"
            return StreamingResponse(generate_stream(), media_type="text/event-stream")
        else:
            response = ChatCompletionResponse(
                choices=[
                    ChatCompletionResponseChoice(
                        index=0,
                        message=Message(role="assistant", content=formatted_response),
                        finish_reason="stop"
                    )
                ]
            )
            logger.info(f"返回给用户的响应是: {response}")
            return JSONResponse(content=response.model_dump)
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


    

if __name__ == '__main__':
    logger.info(f"在端口 {PORT} 上启动服务")
    ## uvicorn 启动服务
    uvicorn.run(app, host="0.0.0.0", port=PORT)
