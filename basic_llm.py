from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from dotenv import load_dotenv
import os

load_dotenv()

def get_openai_chain():
    """Builds an LLMChain using OpenAI's model"""
    prompt = PromptTemplate.from_template("Answer this: {question}")
    llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini")
    return prompt | llm

def get_deepseek_chain():
    """Builds an LLMChain using DeepSeek's model"""
    prompt = PromptTemplate.from_template("Answer this: {question}")
    llm = ChatDeepSeek(api_key=os.getenv("DEEPSEEK_API_KEY"), model="deepseek-chat")
    return prompt | llm

def get_NVIDIA_chain():
    prompt = PromptTemplate.from_template("Answer this: {question}")
    llm = ChatNVIDIA(
        model="deepseek-ai/deepseek-r1",
        api_key=os.getenv("NVIDIA_API_KEY"),
        temperature=0.6,
        top_p=0.7,
        max_tokens=4096,
    )
    return prompt | llm

if __name__ == "__main__":
    question = input("Enter your question: ").strip()

    chain = get_NVIDIA_chain()

    response = chain.invoke({"question": question})
    print(f"\n[Response]:\n{response}")
