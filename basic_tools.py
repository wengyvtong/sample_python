import os
from langchain.agents import AgentType, initialize_agent
from langchain.tools import StructuredTool
from langchain_deepseek import ChatDeepSeek
from pydantic import BaseModel, Field
from typing import Optional
import math
import requests
from dotenv import load_dotenv


class WeatherInput(BaseModel):
    location: str = Field(description="城市名称，例如：北京、上海")
    date: Optional[str] = Field(description="查询日期，格式YYYY-MM-DD，默认今天")
    temperature: float = Field(description="温度值，单位摄氏度")
    wind_speed: int = Field(description="风力等级，1-12级")
    condition: Optional[str] = Field(default="晴",
                                     description="天气状况，例如：晴、多云、雨")
    humidity: Optional[int] = Field(default=None,
                                    description="湿度百分比，0-100之间的整数")


def get_weather(
        location: str,
        temperature: 25.5,
        wind_speed: 3,
        date: Optional[str] = None,
        condition: str = "晴",
        humidity: Optional[int] = 16
) -> str:
    """获取指定位置的天气信息"""

    # 构建天气报告
    report = [
        f"{location} {date} 天气预报",
        f"温度：{temperature}°C",
        f"风力：{wind_speed}级",
        f"天气状况：{condition}"
    ]

    # 添加可选湿度信息
    if humidity is not None:
        report.append(f"湿度：{humidity}%")

    # 添加天气建议
    if temperature > 30:
        report.append("温馨提示：今日高温，注意防暑")
    elif temperature < 10:
        report.append("温馨提示：气温较低，注意保暖")

    if "雨" in condition:
        report.append("提醒：建议携带雨具")

    return "\n".join(report)


# 示例用法：get_weather("北京", 25, 3)

weather_tool = StructuredTool.from_function(
    func=get_weather,
    name="WeatherForecast",
    description="用于获取城市天气预报信息，包含温度、风力、湿度等数据",
    args_schema=WeatherInput
)

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

calculator_tool = StructuredTool.from_function(
    func=calculator,
    name="Calculator",
    description="Useful for performing mathematical calculations. Input should include operation (add, subtract, multiply, divide, power, sqrt) and numbers.",
    args_schema=CalculatorInput
)

load_dotenv()

llm = ChatDeepSeek(api_key=os.getenv("DEEPSEEK_API_KEY"), model="deepseek-chat")


tools = [calculator_tool,weather_tool]

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