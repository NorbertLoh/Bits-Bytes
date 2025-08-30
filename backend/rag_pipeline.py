import json
import os
import pandas as pd
from typing import TypedDict, List, Literal
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import logging

# --- 1. CONFIGURATION ---
# Define all configurations in one place for easy modification
OLLAMA_BASE_URL = "http://25.1.81.74:8080"
OLLAMA_VERIFICATION_BASE_URL = "http://25.1.81.74:8001"
LLM_MODEL = "qwen3:8b"
LLM_VALIDATOR = "qwen3:1.7b"  # Specific model for the validation step
EMBEDDING_MODEL = "nomic-embed-text"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_RETRIES = 3 # Maximum number of retries for the generation step
HALLUCINATION_CONFIDENCE_THRESHOLD = 0.7 # Minimum confidence score to pass the hallucination check

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('app.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# Document paths for loading
DOCUMENT_PATHS = [
    "regulations/18_US_Code_2258A.pdf",
    "regulations/Cali_State_Law_Social_Media_Addication_Act.pdf",
    "regulations/EU_DSA.pdf",
    "regulations/Florida_Online_Protections_Minors.pdf",
    "regulations/Utah_Social_Media_Regulation_Act.pdf",
    "terminologies/terminologies.xlsx"
]

OLLAMA_CHAT_OPTIONS = {
    "num_predict": 2048, # Sets the max tokens to generate
}

class ComplianceStatus(BaseModel):
    """
    Schema for the geo-regulation compliance check.
    """
    feature_type: Literal["Business Driven", "Legal Requirement", "Unclassified"] = Field(
        ...,
        description="Determines if the feature is driven by business needs or legal requirements. If unsure or does not look like a feature, select 'Unclassified'."
    )
    compliance_status: Literal["Compliance Logic Needed", "No Compliance Logic Needed", "Requires Further Review"] = Field(
        ...,
        description="Determines if the feature requires geo-specific compliance logic for legal requirements. If unsure or does not look like a feature, select 'Requires Further Review'."
    )
    supporting_regulations: List[str] = Field(
        ...,
        description="A list of specific regulations or laws that the compliance logic is for. If unsure or does not look like a feature, leave this list empty."
    )
    reasoning: str = Field(
        ...,
        description="A brief explanation of why this compliance status was determined. If the feature is business driven, explain why no compliance logic is needed. If unsure or does not look like a feature, explain why it was classified as such. If no intention for the feature is specified, explain that it requires further review."
    )

class HallucinationCheckResult(BaseModel):
    """
    Structured output for the hallucination check.
    """
    verdict: Literal["Supported", "Not Supported", "Requires Review"] = Field(
        ...,
        description="Whether the reasoning and supporting regulations in the generated answer are fully supported by the provided documents."
    )
    confidence: float = Field(
        ...,
        description="A confidence score from 0.0 to 1.0 indicating the certainty of the verdict. 1.0 means completely certain."
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
                documents = load_excel_as_documents(file_path)
                all_documents.extend(documents)
            else:
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
    """Represents the state of our graph with added guardrail logic."""
    question: str
    memory: list
    documents: List[Document]
    generation: str
    retries: int
    is_supported: bool
    hallucination_verdict: str
    hallucination_confidence: float

def rewrite_question(state: GraphState) -> GraphState:
    """
    Analyzes the user's feature description and generates a list of
    potential geo-compliance areas for investigation.
    """
    print("---ANALYZING FEATURE FOR COMPLIANCE CONCEPTS---")
    question = state["question"]
    memory = state["memory"]
    
    analysis_prompt = ChatPromptTemplate.from_template(
        "You are an AI-powered geo-regulation checker. Your task is to analyze a given feature description and determine if it requires geo-specific compliance actions. \n\n"
        "If it does not seem like a feature, there is no need for a specific area of concern, just state that. \n\n"
        "Based on the following feature description, determine if there are any potential geo-compliance issues, requirements, or areas of concern that would be related. If there is none, just state that. Focus on high-level concepts rather than specific laws. \n\n"
        "---FEATURE DESCRIPTION---"
        "{question}"
        "---ADDITIONAL CONTEXT---"
        "{memory}"
        "\n\n"
        "Answer in a detailed, bulleted list. Each bullet point should start with a specific area of concern (e.g., 'Age Verification', 'Data Privacy', 'Parental Consent') followed by a brief explanation of why this feature might be at risk."
    )

    rewrite_llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL,
        )
    analysis_chain = analysis_prompt | rewrite_llm

    compliance_concepts_response = analysis_chain.invoke({"question": question, "memory": memory})

    rewritten_question_str = compliance_concepts_response.content.strip()
    
    print(f"Original question: '{question}'")
    print(f"Generated compliance concepts:\n{rewritten_question_str}")

    return {"question": rewritten_question_str, "documents": None, "generation": None, "retries": 0, "is_supported": False, "hallucination_verdict": "", "hallucination_confidence": 0.0}

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
    memory = state["memory"]

    prompt_template = (
        "You are an AI-powered geo-regulation checker. Your task is to analyze "
        "the provided context to determine if a feature requires geo-specific compliance actions to meet legal requirement. "
        "If the feature is business driven, select 'No Compliance Logic Needed'. If uncertain, select 'Requires Further Review'. "
        "If it is a feature and no intention is specified, select 'Requires Further Review'. "
        "Your final answer MUST be in the specified JSON format."
        "\n\n"
        "---EXAMPLES---"
        "'Feature reads user location to enforce France's copyright rules (download blocking)' - 'Compliance Logic Needed'"
        "'Geofences feature rollout in US for market testing' - 'No Compliance Logic Needed' (Business decision, not regulatory)'"
        "'A video filter feature is available globally except KR' - 'Requires Further Review' (didn't specify the intention, need human evaluation)"
        "---CONTEXT---"
        "{context}"
        "\n\n"
        "---ADDITIONAL CONTEXT---"
        "{memory}"
        "\n\n"
        "---USER QUESTION---"
        "Here is the feature and feature description to validate:"
        "{question}"
        "\n\n"
    )

    prompt = ChatPromptTemplate.from_template(prompt_template)
    llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL,
        **OLLAMA_CHAT_OPTIONS)
    
    structured_llm = llm.with_structured_output(ComplianceStatus, method='json_schema')
    rag_chain = prompt | structured_llm
    context_str = "\n\n".join([doc.page_content for doc in documents])
    
    generation = rag_chain.invoke({"context": context_str, "question": question, "memory": memory})
    generation_str = generation.model_dump_json(indent=2)

    return {"documents": documents, "question": question, "generation": generation_str}

def check_hallucination(state: GraphState) -> GraphState:
    """
    Validates the generated answer against the retrieved documents using a smaller LLM.
    Returns a structured output with a verdict and confidence.
    """
    print("---CHECKING FOR HALLUCINATIONS WITH VALIDATOR LLM---")
    question = state["question"]
    generation_str = state["generation"]
    documents = state["documents"]

    retries = state.get("retries", 0) + 1
    
    validator_llm = ChatOllama(model=LLM_VALIDATOR, base_url=OLLAMA_VERIFICATION_BASE_URL,
        )

    validator_prompt = ChatPromptTemplate.from_template(
        "You are a validation assistant. Your task is to analyze a 'Generated Answer' against 'Provided Documents' and a 'User Question' based on the following criteria:"
        "Ensure that the reasoning and supporting regulations in the Generated Answer can be found in the Provided Documents."
        "Ensure that there is no hallucination or fabrication of facts in the Generated Answer and no repetition of the User Question."
        "Your final answer MUST be in the specified JSON format with a verdict ('Supported', 'Not Supported', or 'Requires Review') and a confidence score from 0.0 to 1.0. where 1.0 means completely certain."
        "\n\n"
        "---USER QUESTION---"
        "{question}"
        "\n\n"
        "---PROVIDED DOCUMENTS---"
        "{documents}"
        "\n\n"
        "---GENERATED ANSWER---"
        "{generation}"
        "\n\n"
    )

    structured_validator = validator_llm.with_structured_output(HallucinationCheckResult, method='json_schema')
    validator_chain = validator_prompt | structured_validator

    try:
        # Check if the generated string is valid JSON before invoking the validator
        json.loads(generation_str)

        validation_response = validator_chain.invoke({
            "question": question,
            "documents": "\n\n".join([doc.page_content for doc in documents]),
            "generation": generation_str
        })
        is_supported = validation_response.confidence >= HALLUCINATION_CONFIDENCE_THRESHOLD
        verdict = validation_response.verdict
        confidence = validation_response.confidence
        print(f"Hallucination check result (using {LLM_VALIDATOR}): {verdict} with confidence {confidence:.2f}")

    except json.JSONDecodeError as e:
        print(f"JSON parsing failed for generated answer: {e}")
        is_supported = False
        verdict = "Not Supported"
        confidence = 0.0
    except Exception as e:
        print(f"Error during validation: {e}")
        is_supported = False
        verdict = "Requires Review"
        confidence = 0.0

    return {"is_supported": is_supported, "retries": retries, "hallucination_verdict": verdict, "hallucination_confidence": confidence}

def no_solution(state: GraphState) -> GraphState:
    """Provides a structured message when a solution cannot be found after retries."""
    print("---NO SOLUTION FOUND AFTER RETRIES---")
    
    # Create a structured output for a "no solution" scenario
    no_solution_result = ComplianceStatus(
        feature_type="Unclassified",
        compliance_status="Requires Further Review",
        supporting_regulations=[],
        reasoning="Unable to provide a verified compliance status after multiple retries. The provided documents may not contain enough information."
    )
    
    return {"generation": no_solution_result.model_dump_json(indent=2)}

# --- 4. BUILD AND COMPILE THE GRAPH ---
def route_check(state: GraphState):
    """Conditional router based on validation check and retry count."""
    is_supported = state["is_supported"]
    retries = state.get("retries", 0)
    
    if is_supported:
        return "end"
    elif retries >= MAX_RETRIES:
        return "no_solution"
    else:
        print(f"---RETRYING GENERATION, ATTEMPT {retries} OF {MAX_RETRIES}---")
        return "generate"

workflow = StateGraph(GraphState)

workflow.add_node("rewrite", rewrite_question)
workflow.add_node("retrieve", retrieve_documents)
workflow.add_node("generate", generate_answer)
workflow.add_node("check", check_hallucination)
workflow.add_node("no_solution", no_solution)

workflow.set_entry_point("rewrite")
workflow.add_edge("rewrite", "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", "check")

workflow.add_conditional_edges(
    "check",
    route_check,
    {
        "end": END,
        "no_solution": "no_solution",
        "generate": "generate"
    }
)
workflow.add_edge("no_solution", END)

app_pipeline = workflow.compile()

def run_rag_pipeline(question: str, memory: list) -> str:
    """Function to encapsulate running the langgraph pipeline."""
    inputs = {"question": question, "memory": memory, "retries": 0, "is_supported": False, "hallucination_verdict": "", "hallucination_confidence": 0.0}
    final_state = app_pipeline.invoke(inputs)

    logger.info(f"Feature: {question}, Answer: {json.dumps(final_state['generation'], indent=2)}")
    return final_state['generation']
