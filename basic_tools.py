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
    location: str = Field(description="City name or location for weather forecast")


def get_weather_forecast(location: str) -> str:
    """Get the current weather and forecast for a location."""
    try:
        return f"Weather forecast for {location}: Sunny with a high of 25°C and low of 15°C. 10% chance of precipitation."
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"

weather_tool = StructuredTool.from_function(
    func=get_weather_forecast,
    name="WeatherForecast",
    description="Get current weather and forecast for a specific location. Provide the city name or location.",
    args_schema=WeatherInput  # This connects the schema to the function
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