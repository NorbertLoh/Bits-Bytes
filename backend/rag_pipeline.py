import os
import pandas as pd
from typing import TypedDict, List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langgraph.graph import StateGraph, END

# --- 1. CONFIGURATION ---
# Define all configurations in one place for easy modification
OLLAMA_BASE_URL = "http://25.1.81.74:8080"
LLM_MODEL = "qwen3:8b"
EMBEDDING_MODEL = "nomic-embed-text"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Document paths for loading
DOCUMENT_PATHS = [
    "regulations/18_US_Code_2258A.pdf",
    "regulations/Cali_State_Law_Social_Media_Addication_Act.pdf",
    "regulations/EU_DSA.pdf",
    "regulations/Florida_Online_Protections_Minors.pdf",
    "regulations/Utah_Social_Media_Regulation_Act.pdf",
    "terminologies/terminologies.xlsx"
]

# --- 2. DOCUMENT LOADING AND PROCESSING ---
def load_excel_as_documents(excel_path: str) -> List[Document]:
    """Loads an Excel file and converts each row into a LangChain Document."""
    try:
        df = pd.read_excel(excel_path)
        documents = []
        for index, row in df.iterrows():
            # Create a combined string from all row values
            content = ", ".join([f"{col}: {value}" for col, value in row.items()])
            # Store the entire row as metadata
            metadata = row.to_dict()
            documents.append(Document(page_content=content, metadata=metadata))
        return documents
    except Exception as e:
        print(f"Error loading Excel file {excel_path}: {e}")
        return []

def load_documents_from_paths(file_paths: List[str]) -> List[Document]:
    """Loads documents from a list of file paths based on file extension."""
    all_documents = []
    for file_path in file_paths:
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()
        
        try:
            if extension == ".xlsx":
                # Use a dedicated function for Excel files
                documents = load_excel_as_documents(file_path)
                all_documents.extend(documents)
            else:
                # Use standard LangChain loaders for other file types
                if extension == ".txt":
                    loader = TextLoader(file_path)
                elif extension == ".pdf":
                    loader = PyPDFLoader(file_path)
                elif extension == ".docx":
                    loader = Docx2txtLoader(file_path)
                else:
                    print(f"Unsupported file type: {extension} for path: {file_path}")
                    continue
                all_documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    return all_documents

# Load, split, and create vector store
all_documents = load_documents_from_paths(DOCUMENT_PATHS)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
texts = text_splitter.split_documents(all_documents)

embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)
vectorstore = FAISS.from_documents(texts, embeddings)
retriever = vectorstore.as_retriever()

# --- 3. LANGGRAPH SETUP ---
class GraphState(TypedDict):
    """Represents the state of our graph."""
    question: str
    documents: List[Document]
    generation: str

def retrieve_documents(state: GraphState) -> GraphState:
    """Retrieves documents based on the question and updates the state."""
    print("---RETRIEVING DOCUMENTS---")
    question = state["question"]
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}

def generate_answer(state: GraphState) -> GraphState:
    """Generates an answer using retrieved documents and updates the state."""
    print("---GENERATING ANSWER---")
    question = state["question"]
    documents = state["documents"]
    
    # Simple RAG prompt template
    prompt_template = (
        "Use the following pieces of context to answer the question at the end.\n"
        "If you don't know the answer, just say that you don't know, don't try to make up an answer.\n"
        "Context: {context}\n"
        "Question: {question}\n"
        "Helpful Answer:"
    )
    
    # Format the context for the prompt
    context_str = "\n\n".join([doc.page_content for doc in documents])
    prompt = prompt_template.format(context=context_str, question=question)

    # Invoke the LLM
    llm = OllamaLLM(model=LLM_MODEL, base_url=OLLAMA_BASE_URL)
    generation = llm.invoke(prompt)
    
    return {"documents": documents, "question": question, "generation": generation}

# --- 4. BUILD AND COMPILE THE GRAPH ---
workflow = StateGraph(GraphState)
workflow.add_node("retrieve", retrieve_documents)
workflow.add_node("generate", generate_answer)
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)
app_pipeline = workflow.compile()

def run_rag_pipeline(question: str) -> str:
    """Function to encapsulate running the langgraph pipeline."""
    inputs = {"question": question}
    final_state = app_pipeline.invoke(inputs)
    return final_state['generation']