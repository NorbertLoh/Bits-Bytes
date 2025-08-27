import json
import os
import pandas as pd
from typing import TypedDict, List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from typing import List, Literal

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

class ComplianceStatus(BaseModel):
    """
    Schema for the geo-regulation compliance check.
    """
    feature_type: Literal["Business Driven", "Legal Requirement", "Unclassified"] = Field(
        ...,
        description="Determines if the feature is driven by business needs or legal requirements."
    )
    compliance_status: Literal["Compliance Logic Needed", "No Compliance Logic Needed", "Requires Further Review"] = Field(
        ...,
        description="Determines if the feature requires geo-specific compliance logic for legal requirements."
    )
    supporting_regulations: List[str] = Field(
        ...,
        description="A list of specific regulations or laws that the compliance logic is for. If feature type is unclassified or not enough information, this can be an empty list."
    )
    reasoning: str = Field(
        ...,
        description="A brief explanation of why this compliance status was determined. If the feature is business driven, explain why no compliance logic is needed."
    )

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

def rewrite_question(state: GraphState) -> GraphState:
    """
    Analyzes the user's feature description and generates a list of
    potential geo-compliance areas for investigation.
    """
    print("---ANALYZING FEATURE FOR COMPLIANCE CONCEPTS---")
    question = state["question"]
    
    analysis_prompt = ChatPromptTemplate.from_template(
        "You are an AI-powered geo-regulation checker. Your task is to analyze a given feature description and determine if it requires geo-specific compliance actions. \n\n"
        "Based on the following feature description, determine if there are any potential geo-compliance issues, requirements, or areas of concern that would be related. If there is none, just state that. Focus on high-level concepts rather than specific laws. \n\n"
        "---FEATURE DESCRIPTION---"
        "{question}"
        "\n\n"
        "Answer in a detailed, bulleted list. Each bullet point should start with a specific area of concern (e.g., 'Age Verification', 'Data Privacy', 'Parental Consent') followed by a brief explanation of why this feature might be at risk."
    )

    rewrite_llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL)
    analysis_chain = analysis_prompt | rewrite_llm
    
    compliance_concepts_response = analysis_chain.invoke({"question": question})
    
    # The rewritten query for retrieval is the LLM's full response.
    # It contains all the concepts identified.
    rewritten_question_str = compliance_concepts_response.content.strip()
    
    print(f"Original question: '{question}'")
    print(f"Generated compliance concepts:\n{rewritten_question_str}")

    return {"question": rewritten_question_str, "documents": None, "generation": None}


def retrieve_documents(state: GraphState) -> GraphState:
    """Retrieves documents based on the question and updates the state."""
    print("---RETRIEVING DOCUMENTS---")
    question = state["question"]
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}

def generate_answer(state: GraphState) -> GraphState:
    """Generates a structured answer using retrieved documents and updates the state."""
    print("---GENERATING STRUCTURED ANSWER---")
    question = state["question"]
    documents = state["documents"]

    # Simple RAG prompt template
    prompt_template = (
        "You are an AI-powered geo-regulation checker. Your task is to analyze "
        "the provided context to determine if a feature requires geo-specific compliance actions to meet legal requirement. "
        "If the feature is business driven, select 'No Compliance Logic Needed'. If uncertain, select 'Requires Further Review'. "
        "Only use the information provided in the context to make your determination. "
        "Your final answer MUST be in the specified JSON format."
        "\n\n"
        "---EXAMPLES---"
        "'Feature reads user location to enforce France's copyright rules (download blocking)' - 'Compliance Logic Needed'"
        "'Geofences feature rollout in US for market testing' - 'No Compliance Logic Needed' (Business decision, not regulatory)'"
        "'A video filter feature is available globally except KR' - 'Requires Further Review' (didn't specify the intention, need human evaluation)"
        "---CONTEXT---"
        "{context}"
        "\n\n"
        "---USER QUESTION---"
        "Here is the feature and feature description to validate:"
        "{question}"
        "\n\n"
    )

    # Convert the prompt to a ChatPromptTemplate
    prompt = ChatPromptTemplate.from_template(prompt_template)
    
    # Initialize the LLM
    llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL)
    
    # Create the structured output chain
    # The `with_structured_output` method automatically handles the JSON schema for you.
    structured_llm = llm.with_structured_output(ComplianceStatus, method='json_schema')
    
    # Create the chain to invoke
    rag_chain = prompt | structured_llm
    
    # Format the context for the prompt
    context_str = "\n\n".join([doc.page_content for doc in documents])
    
    # Invoke the chain to get the structured response
    generation = rag_chain.invoke({"context": context_str, "question": question})

    # The result is a Pydantic object, which you can easily convert to a dictionary or JSON
    # For your current pipeline, you'll need a string.
    # Note: If your graph used a more complex state, you could pass the Pydantic object directly.
    # For now, let's convert it to a pretty JSON string.
    generation_str = generation.model_dump_json(indent=2)
    return {"documents": documents, "question": question, "generation": generation_str}

# --- 4. BUILD AND COMPILE THE GRAPH ---
workflow = StateGraph(GraphState)

workflow.add_node("rewrite", rewrite_question)
workflow.add_node("retrieve", retrieve_documents)
workflow.add_node("generate", generate_answer)

workflow.set_entry_point("rewrite")
workflow.add_edge("rewrite", "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

app_pipeline = workflow.compile()

def run_rag_pipeline(question: str) -> str:
    """Function to encapsulate running the langgraph pipeline."""
    inputs = {"question": question}
    final_state = app_pipeline.invoke(inputs)
    print(final_state)
    return final_state['generation']