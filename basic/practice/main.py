
import logging
from contextlib import asynccontextmanager
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
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

class ChatCompleteRequest(BaseModel):
    messages: List[Message]
    stream: Optional[bool] = False

async def chat_compltetions(request: )
    

if __name__ == '__main__':
    logger.info(f"在端口 {PORT} 上启动服务")
    ## uvicorn 启动服务
    uvicorn.run(app, host="0.0.0.0", port=PORT)
