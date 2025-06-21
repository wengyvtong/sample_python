from langchain.agents import initialize_agent, AgentType, Tool
from langchain.memory import ConversationBufferMemory
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader  # Updated import for PDF loading
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from dotenv import load_dotenv
import os
# Langfuse imports
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

load_dotenv()

# Initialize Langfuse
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)
# Create Langfuse callback handler
langfuse_handler = CallbackHandler()

# llm = ChatDeepSeek(api_key=os.getenv("DEEPSEEK_API_KEY"), model="deepseek-chat")
llm = ChatNVIDIA(
#   model="deepseek-ai/deepseek-r1",
  model="meta/llama-3.3-70b-instruct",
  api_key=os.getenv("NVIDIA_API_KEY_LLAMA33"),
  temperature=0.6,
  top_p=0.7,
  max_tokens=4096,
)

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

def doc_tool(query: str) -> str:
    """Search the knowledge base for an answer to the question in Chinese."""
    docs = TextLoader("brainrent_part1.txt", encoding='utf-8').load()
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    qa_chain = load_qa_chain(llm=llm, chain_type="stuff")
    return qa_chain.run(input_documents=chunks, question=query)

tools = [
    Tool(
        name="KnowledgeBase",
        func=doc_tool,
        description="Useful for answering questions about Brainrent."
    ),
]

# 4. Initialize the agent with tools and memory
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)

if __name__ == "__main__":
    while True:
        query = input("\nEnter your question (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        result = agent.invoke({"input": query}, config={"callbacks": [langfuse_handler]})
        print(f"Result: {result['output']}")