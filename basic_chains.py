from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_core.runnables import RunnableLambda, RunnableMap

from dotenv import load_dotenv
import os

load_dotenv()

def get_summary_prompt():
    return PromptTemplate.from_template("Summarize the following(用中文):\n\n{text}")


def get_title_prompt():
    return PromptTemplate.from_template("Create a 5-word title for this(用中文):\n\n{summary}")

def get_english_prompt():
    return PromptTemplate.from_template("将中文翻译成英文:\n\n{text}")

def build_hyper_chain():
    llm = ChatDeepSeek(api_key=os.getenv("DEEPSEEK_API_KEY"), model="deepseek-chat", temperature=0.7)
    summarize_chain = get_summary_prompt() | llm
    title_chain = get_title_prompt() | llm
    english_chain = get_english_prompt() | llm

    def chain_fn(inputs):
        summary = summarize_chain.invoke({"text": inputs["text"]})
        title = title_chain.invoke({"summary": summary})
        english = english_chain.invoke({"text": inputs["text"]})
        return {"summary": summary, "title": title, "english": english}
    return RunnableLambda(chain_fn)


if __name__ == "__main__":
    full_text = input("Paste your paragraph:\n\n")

    chain = build_hyper_chain()
    outputs = chain.invoke({"text": full_text})

    # Display outputs
    print(f"\n[Summary]: {outputs['summary'].content}")
    print(f"\n[Title]: {outputs['title'].content}")
    print(f"\n[English]: {outputs['english'].content}")