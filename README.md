知识库工具：基于脑租公司相关文档
API 工具：调用Open-Meteo API进行天气查询
本地函数工具：实现一个计算器自定义 Python 函数
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
