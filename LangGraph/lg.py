from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM

from typing import TypedDict, List
from langchain_core.documents import Document

from langgraph.graph import StateGraph, END

documents_as_strings = [
    "The capital of France is Paris. It is known for the Eiffel Tower.",
    "The current monarch of the United Kingdom is King Charles III.",
    "The powerhouse of the cell is the mitochondria.",
]

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.create_documents(documents_as_strings)

# Create Vector Store
embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://25.1.81.74:8080")
vectorstore = FAISS.from_documents(texts, embeddings)
retriever = vectorstore.as_retriever()

# LangGraph Node and Edge Definitions
class GraphState(TypedDict):
    question: str
    documents: List[Document]
    generation: str

def retrieve_documents(state):
    """
    Retrieves documents based on the question.

    Args:
        state (dict): The current graph state.

    Returns:
        dict: New key-value pairs to add to the state.
    """
    print("---RETRIEVING DOCUMENTS---")
    question = state["question"]
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}

def generate_answer(state):
    """
    Generates an answer using the retrieved documents.

    Args:
        state (dict): The current graph state.

    Returns:
        dict: New key-value pairs to add to the state.
    """
    print("---GENERATING ANSWER---")
    question = state["question"]
    documents = state["documents"]

    # RAG prompt
    prompt = f"""Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Context: {documents}
    Question: {question}
    Helpful Answer:"""

    # LLM
    llm = OllamaLLM(model="qwen3:8b", base_url="http://25.1.81.74:8080")
    generation = llm.invoke(prompt)
    return {"documents": documents, "question": question, "generation": generation}

workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("retrieve", retrieve_documents)
workflow.add_node("generate", generate_answer)

# Build the graph
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

# Compile the graph
app = workflow.compile()

inputs = {"question": "What is the capital of France?"}

# This runs the graph to completion and returns the final state
final_state = app.invoke(inputs)

print(final_state)

# --- DEBUG PRINT: See the full final state ---
print(f"Final state after graph execution: {final_state}")

# This line is where your KeyError happens, because 'generation' isn't in final_state
print(f"Final Answer: {final_state['generation']}")