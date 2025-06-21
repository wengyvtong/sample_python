agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

知识库工具：基于脑租公司相关文档
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

API 工具：调用Open-Meteo API进行天气查询
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

本地函数工具：实现一个计算器自定义 Python 函数
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

能记忆
结果：
Enter your question (or 'exit' to quit): 青岛天气如何


> Entering new AgentExecutor chain...
Action:
```
{
  "action": "WeatherForecast",
  "action_input": "青岛"
}
```

Observation: 错误：找不到位置 '青岛'，请检查城市名称是否正确
Thought:可能是由于城市名称不正确或不完整导致的错误。可以尝试使用更详细的城市名称或检查拼写是否正确。
Action:
```
{
  "action": "WeatherForecast",
  "action_input": "青岛市"
}
```

Observation: 错误：找不到位置 '青岛市'，请检查城市名称是否正确
Thought:可能是由于城市名称不正确或不完整导致的错误。可以尝试使用更详细的城市名称或检查拼写是否正确。另外，也可以尝试使用英文名称或拼音名称来查询天气。
Action:
```
{
  "action": "WeatherForecast",
  "action_input": "Qingdao"
}
```
Observation: ShandongQingdao天气预报：

【今天】
- 天气: 阴
- 温度: 21.7°C ~ 28.5°C
- 降水: 0.0 mm
- 风速: 13.8 km/h
- 风向: 南风

【明天】
- 天气: 阴
- 温度: 21.8°C ~ 28.5°C
- 降水: 0.0 mm
- 风速: 14.1 km/h
- 风向: 南风

【后天】
- 天气: 阴
- 温度: 21.4°C ~ 27.9°C
- 降水: 0.0 mm
- 风速: 14.9 km/h
- 风向: 南风

数据来源：Open-Meteo（更新于2025-06-21 14:31)
Thought:Action:
```
{
  "action": "Final Answer",
  "action_input": "青岛市的天气预报为：今天和明天都是阴天，温度范围为21.7°C ~ 28.5°C，降水为0.0 mm，风速为13.8 km/h和14.1 km/h，风向为南风。后天也是阴天，温度范围为21.4°C ~ 27.9°C，降水为0.0 mm，风速为14.9 km/h，风向为南风。"
}
```

> Finished chain.
Result: 青岛市的天气预报为：今天和明天都是阴天，温度范围为21.7°C ~ 28.5°C，降水为0.0 mm，风速为13.8 km/h和14.1 km/h，风向为南风。后天也是阴天，温度范围为21.4°C ~ 27.9°C，降水为0.0 mm，风速为14.9 km/h，风向为南风。

Enter your question (or 'exit' to quit): 脑租公司业务是什么


> Entering new AgentExecutor chain...
Action:
```
{
  "action": "KnowledgeBase",
  "action_input": "Brainrent business"
}
```
D:\GitHub\sample_python\big_homework.py:210: LangChainDeprecationWarning: This class is deprecated. See the following migration guides for replacements based on `chain_type`:
stuff: https://python.langchain.com/docs/versions/migrating_chains/stuff_docs_chain
map_reduce: https://python.langchain.com/docs/versions/migrating_chains/map_reduce_chain
refine: https://python.langchain.com/docs/versions/migrating_chains/refine_chain
map_rerank: https://python.langchain.com/docs/versions/migrating_chains/map_rerank_docs_chain

See also guides on retrieval and question-answering here: https://python.langchain.com/docs/how_to/#qa-with-rag
  qa_chain = load_qa_chain(llm=llm, chain_type="stuff")
D:\GitHub\sample_python\big_homework.py:211: LangChainDeprecationWarning: The method `Chain.run` was deprecated in langchain 0.1.0 and will be removed in 1.0. Use :meth:`~invoke` instead.
  return qa_chain.run(input_documents=chunks, question=query)

Observation: 根据提供的信息，BrainRent 的业务主要围绕“思维即服务（TaaS，Thinking as a Service）”模式展开。他们提供的服务包括：

1. 学术研究支持
2. 企业决策咨询
3. 创新创意生成
4. 复杂问题建模与推理

用户可以通过移动应用或网页平台提交问题，BrainRent 的系统会根据问题类型匹配最适合的“思维单元”（即高性能的AI大脑或真人思维专家），在约定时间内返回详尽的思考成果。

BrainRent 的核心产品是“云脑池（BrainCloud）”，它是一个整合了数千名训练有素的专家与数百个高智能AI Agent的分布式思维网络。用户可以选择使用“AI智能思维”、“人类专家思维”或“混合思维模式”，以满足不同的预算和精准度要求。
Thought:根据BrainRent的业务介绍，他们提供的服务包括学术研究支持、企业决策咨询、创新创意生成和复杂问题建模与推理等。他们的核心产品是“云脑池（BrainCloud）”，它是一个整合了数千名训练有素的专家与数百个高智能AI Agent的分布式思维网络。用户可以根据自己的需求选择使用“AI智能思维”、“人类专家思维”或“混合思维模式”。

Action:
```
{
  "action": "Final Answer",
  "action_input": "BrainRent 的业务主要围绕 \"思维即服务（TaaS，Thinking as a Service）\" 模式展开，提供学术研究支持、企业决策咨询、创新创意生成和复杂问题建模与推理等服务。他们的核心产品是 \"云脑池（BrainCloud）\"，它是一个整合了数千名训练有素的专家与数百个高智能AI Agent的分布式思维网络。"
}
```

> Finished chain.
Result: BrainRent 的业务主要围绕 "思维即服务（TaaS，Thinking as a Service）" 模式展开，提供学术研究支持、企业决策咨询、创新创意生成和复杂问题建模与推理等服务。他们的核心产品是 "云脑池（BrainCloud）"，它是一个整合了数千名训练有素的专家与数百个高智能AI Agent的分布式思维网络。

Enter your question (or 'exit' to quit): 3+6等于几


> Entering new AgentExecutor chain...
Action:
```
{
  "action": "Calculator",
  "action_input": {
    "operation": "add",
    "a": 3,
    "b": 6
  }
}
```

Observation: 3.0 + 6.0 = 9.0
Thought:The result of the calculation is already obtained, which is 9.0.

Action:
```
{
  "action": "Final Answer",
  "action_input": "9"
}
```

> Finished chain.
Result: 9
