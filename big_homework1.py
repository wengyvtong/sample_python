import os
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.tools import StructuredTool
from langchain.memory import ConversationBufferMemory
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from pydantic import BaseModel, Field
from typing import Optional
import math
from dotenv import load_dotenv
# Langfuse imports for interaction tracking
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
import requests
from typing import Dict, List, Tuple
import datetime
from langchain.agents import ZeroShotAgent, AgentExecutor

# 加载环境变量
load_dotenv()

# # 初始化Langfuse（用于AI交互追踪）
# langfuse = Langfuse(
#     public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
#     secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
#     host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
# )
# langfuse_handler = CallbackHandler()  # Langfuse回调处理器

# 1. 定义天气工具
class WeatherInput(BaseModel):
    location: str = Field(description="城市名称或位置")


def get_weather_forecast(location: str) -> str:
    """获取指定位置的天气预报（使用Open-Meteo API）"""
    try:
        # 第一步：地理编码 - 将位置名称转换为经纬度
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return f"错误：找不到位置 '{location}'，请检查城市名称是否正确"

        location_data = geo_data["results"][0]
        latitude = location_data["latitude"]
        longitude = location_data["longitude"]
        city_name = location_data["name"]
        country = location_data.get("country", "")
        admin1 = location_data.get("admin1", "")

        # 第二步：获取天气预报数据
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={latitude}&longitude={longitude}&"
            "daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,"
            "windspeed_10m_max,winddirection_10m_dominant&"
            "timezone=auto&forecast_days=3"
        )
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        if "error" in weather_data:
            return f"错误：获取天气数据失败 - {weather_data['reason']}"

        # 第三步：解析天气数据
        daily = weather_data["daily"]
        time_list = daily["time"]
        weather_codes = daily["weathercode"]
        temp_max = daily["temperature_2m_max"]
        temp_min = daily["temperature_2m_min"]
        precipitation = daily["precipitation_sum"]
        wind_speed = daily["windspeed_10m_max"]
        wind_direction = daily["winddirection_10m_dominant"]

        # 第四步：天气代码转中文描述
        def weather_code_to_text(code: int) -> str:
            """将WMO天气代码转换为中文描述"""
            weather_map = {
                0: "晴",
                1: "晴间多云",
                2: "多云",
                3: "阴",
                45: "雾",
                48: "冻雾",
                51: "小雨",
                53: "中雨",
                55: "大雨",
                56: "冻雨",
                57: "强冻雨",
                61: "小雨",
                63: "中雨",
                65: "大雨",
                66: "冰雹",
                67: "冰雹",
                71: "小雪",
                73: "中雪",
                75: "大雪",
                77: "冰粒",
                80: "短时小雨",
                81: "短时中雨",
                82: "短时大雨",
                85: "短时小雪",
                86: "短时大雪",
                95: "雷阵雨",
                96: "雷暴伴冰雹",
                99: "强雷暴伴冰雹"
            }
            return weather_map.get(code, "未知天气")

        # 第五步：风向代码转中文描述
        def wind_direction_to_text(degrees: float) -> str:
            """将风向角度转换为中文描述"""
            directions = [
                (0, 22.5, "北风"),
                (22.5, 67.5, "东北风"),
                (67.5, 112.5, "东风"),
                (112.5, 157.5, "东南风"),
                (157.5, 202.5, "南风"),
                (202.5, 247.5, "西南风"),
                (247.5, 292.5, "西风"),
                (292.5, 337.5, "西北风"),
                (337.5, 360, "北风")
            ]
            for min_deg, max_deg, direction in directions:
                if min_deg <= degrees < max_deg:
                    return direction
            return "未知风向"

        # 第六步：构建天气报告
        location_str = f"{admin1}{city_name}" if admin1 else f"{country}{city_name}"
        result = f"{location_str}天气预报：\n"

        # 获取今天、明天、后天的日期
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        day_after = today + datetime.timedelta(days=2)

        # 日期格式化
        date_formats = {
            today: "今天",
            tomorrow: "明天",
            day_after: "后天"
        }

        # 处理三天的天气数据
        for i in range(3):
            date = datetime.date.fromisoformat(time_list[i])
            day_name = date_formats.get(date, date.strftime("%m月%d日"))

            result += f"\n【{day_name}】\n"
            result += f"- 天气: {weather_code_to_text(weather_codes[i])}\n"
            result += f"- 温度: {temp_min[i]}°C ~ {temp_max[i]}°C\n"
            result += f"- 降水: {precipitation[i]} mm\n"
            result += f"- 风速: {wind_speed[i]} km/h\n"
            result += f"- 风向: {wind_direction_to_text(wind_direction[i])}\n"

        result += f"\n数据来源：Open-Meteo（更新于{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})"
        return result

    except Exception as e:
        return f"错误：获取天气数据时发生异常 - {str(e)}"


# 2. 定义计算器工具
class CalculatorInput(BaseModel):
    operation: str = Field(description="Mathematical operation: add, subtract, multiply, divide, power, sqrt")
    a: float = Field(description="First number")
    b: Optional[float] = Field(default=None, description="Second number (not required for sqrt)")


def calculator(operation: str, a: float, b: Optional[float] = None) -> str:
    """Perform basic arithmetic operations."""
    op = operation.lower()

    if op == "add":
        return f"{a} + {b} = {a + b}"
    elif op == "subtract":
        return f"{a} - {b} = {a - b}"
    elif op == "multiply":
        return f"{a} * {b} = {a * b}"
    elif op == "divide":
        if b == 0:
            return "Error: Division by zero"
        return f"{a} / {b} = {a / b}"
    elif op == "power":
        return f"{a}^{b} = {a ** b}"
    elif op == "sqrt":
        if a < 0:
            return "Error: Cannot take square root of negative number"
        return f"sqrt({a}) = {math.sqrt(a)}"
    else:
        return f"Unknown operation: {op}"

# 3. 定义文档问答工具
def doc_tool(query: str) -> str:
    """在知识库中搜索问题的答案"""
    try:
        # 加载文本文件
        docs = TextLoader("brainrent_part1.txt", encoding='utf-8').load()

        # 分割文本
        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_documents(docs)

        # 创建问答链
        qa_chain = load_qa_chain(llm=llm, chain_type="stuff")
        return qa_chain.run(input_documents=chunks, question=query)
    except Exception as e:
        return f"文档查询出错: {str(e)}"


# 初始化AI模型（使用NVIDIA的Llama 3 70B）
llm = ChatNVIDIA(
    model="meta/llama-3.3-70b-instruct",
    api_key=os.getenv("NVIDIA_API_KEY_LLAMA33"),
    temperature=0.6,  # 控制创造性（0-1，值越高回答越多样）
    top_p=0.7,  # 控制多样性（0-1，值越高词汇选择范围越广）
    max_tokens=4096,  # 最大输出长度
)

# 创建对话记忆
memory = ConversationBufferMemory(
    memory_key="chat_history",  # 记忆存储键名
    return_messages=True  # 返回完整消息而不仅是文本
)

# 创建工具集
weather_tool = StructuredTool.from_function(
    func=get_weather_forecast,
    name="WeatherForecast",
    description="获取特定位置的天气预报，需提供城市名或位置",
    args_schema=WeatherInput
)

calculator_tool = StructuredTool.from_function(
    func=calculator,
    name="Calculator",
    description="Useful for performing mathematical calculations. Input should include operation (add, subtract, multiply, divide, power, sqrt) and numbers.",
    args_schema=CalculatorInput
)

knowledge_tool = Tool(
    name="KnowledgeBase",
    func=doc_tool,
    description="用于回答关于Brainrent的问题"
)

# 组合所有工具
tools = [calculator_tool, weather_tool, knowledge_tool]

# 创建智能代理
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

if __name__ == "__main__":
    while True:
        query = input("\nEnter your question (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        result = agent.invoke(query)
        print(f"Result: {result['output']}")
