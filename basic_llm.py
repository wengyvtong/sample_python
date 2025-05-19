from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain_deepseek import ChatDeepSeek

from dotenv import load_dotenv
import os

load_dotenv()

def get_openai_chain():
    """Builds an LLMChain using OpenAI's model"""
    prompt = PromptTemplate.from_template("Answer this: {question}")
    llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini")
    return LLMChain(llm=llm, prompt=prompt)

def get_deepseek_chain():
    """Builds an LLMChain using DeepSeek's model"""
    prompt = PromptTemplate.from_template("Answer this: {question}")
    llm = ChatDeepSeek(api_key=os.getenv("DEEPSEEK_API_KEY"), model="deepseek-chat")
    return LLMChain(llm=llm, prompt=prompt)

if __name__ == "__main__":
    question = input("Enter your question: ").strip()

    chain = get_deepseek_chain()


    response = chain.run({"question": question})
    print(f"\n[Response]:\n{response}")
