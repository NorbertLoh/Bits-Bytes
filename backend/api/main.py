from io import BytesIO
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from rag_pipeline import run_rag_pipeline

app = FastAPI(title="RAG Pipeline API")

# --- CORS Middleware Configuration ---
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True, # Allow cookies and credentials with the request
    allow_methods=["*"],    # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allow all headers
)

# Pydantic model for request body
class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Endpoint to validate a feature from the text area to the RAG pipeline.
    """
    try:
        answer = run_rag_pipeline(request.question)
        print(answer)
        return {"question": request.question, "answer": answer}
    except Exception as e:
        # Basic error handling
        return {"error": str(e), "message": "An error occurred while processing your request."}, 500
    
@app.post("/upload_and_process")
async def upload_and_process_excel(file: UploadFile = File(...)):
    """
    Endpoint to upload an Excel file, process each row with the RAG pipeline,
    and return a new Excel file with the results.
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only Excel files (.xlsx, .xls) are allowed.")

    try:
        # Read the uploaded Excel file into a pandas DataFrame
        df = pd.read_excel(BytesIO(await file.read()))

        results = []
        errors = []
        errors_idx = []

        # Iterate through each row of the DataFrame
        for index, row in df.iterrows():
            try:
                # Convert the row to a dictionary to pass to the pipeline
                row_dict = row.to_dict()
                
                # Call the RAG pipeline for the current row's data
                pipeline_result = run_rag_pipeline(row_dict)
                
                # Append the pipeline result to our results list
                results.append(pipeline_result)
            except Exception as e:
                # If an error occurs, record it with the row index
                errors.append(str(e))
                errors_idx.append(index)

        # Create a new DataFrame from the results
        # We assume the pipeline returns a dictionary for each row
        results_df = pd.DataFrame(results)

        # Concatenate the original DataFrame with the results DataFrame
        processed_df = pd.concat([df, results_df], axis=1)

        # Write the new DataFrame to a BytesIO object
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            processed_df.to_excel(writer, index=False, sheet_name='Processed_Data')
        
        output.seek(0)

        # Return the new Excel file and the errors as a JSON response
        response_content = {
            "message": "File processed successfully.",
            "errors": errors,
            "errors_idx": errors_idx,
            "file": output.getvalue().hex() # Or you can return as a stream
        }
        
        return response_content
    
    except Exception as e:
        # General error handling for the entire process
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")