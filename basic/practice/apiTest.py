import json
import logging
import requests

# 设置日志模版
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

url = "http://localhost:8082/v1/chat/completions"
headers = {"Content-Type": "application/json"}


stream_flag = False

input_text = "有没有土豪套餐"

data = {
    "messages": [{"role": "user", "content": input_text}],
    "stream": stream_flag,
    "userId":"123",
    "conversationId":"123"
}


if stream_flag:
    try:
        with requests.post(url, stream=True, headers=headers, data=json.dumps(data)) as response:
            for line in response.iter_lines():
                if line:
                    json_str = line.decode('utf-8').strip("data: ")
                    if not json_str:
                        logger.info(f"收到空字符串，跳过...")
                        continue
                    if json_str.startswith('{') and json_str.endswith('}'):
                        try:
                            data = json.loads(json_str)
                            if data['choices'][0]['finish_reason'] == "stop":
                                logger.info(f"接收JSON数据结束")
                            else:
                                logger.info(f"流式输出，响应内容是: {data['choices'][0]['delta']['content']}")
                        except json.JSONDecodeError as e:
                            logger.info(f"JSON解析错误: {e}")
                    else:
                        print(f"无效JSON格式: {json_str}")
    except Exception as e:
        print(f"请求异常: {e}")
else:
    response = requests.post(url, headers=headers, data=json.dumps(data))
    logger.info(f"响应状态码: {response.status_code}")
    logger.info(f"响应内容: {response.text}")
    response.raise_for_status()  # 如果请求失败会抛出异常
    resp_json = response.json()
    if 'choices' not in resp_json:
        raise KeyError(f"响应中缺少 choices 字段，实际响应: {resp_json}")
    content = resp_json['choices'][0]['message']['content']
    logger.info(f"非流式输出，响应内容是：{content}\n")
