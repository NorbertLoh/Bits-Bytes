from io import BytesIO
import json
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
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
    memory: list

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Endpoint to validate a feature from the text area to the RAG pipeline.
    """
    try:
        answer = run_rag_pipeline(request.question, request.memory)
        print(answer)
        return {"question": request.question, "answer": answer}
    except Exception as e:
        # Basic error handling
        return {"error": str(e), "message": "An error occurred while processing your request."}, 500
    
@app.post("/excel")
async def upload_and_process_excel(file: UploadFile = File(...)):
    """
    Endpoint to upload an Excel file, process each row with the RAG pipeline,
    and return a new Excel file with the results.
    """
    # logger.info(f"Received file upload: {file.filename}")

    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    
    allowed_types = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only Excel files (.xlsx, .xls) are allowed.")

    try:
        # Read the uploaded Excel file into a pandas DataFrame
        excel_data = await file.read()
        df = pd.read_excel(BytesIO(excel_data))
        # logger.info(f"Successfully read Excel file with {len(df.index)} rows.")
        
        memory = []
        results = []
        errors = []
        errors_idx = []

        # Iterate through each row of the DataFrame
        for index, row in df.iterrows():
            try:
                # Get the relevant data from the row
                feature_name = str(row.get("feature_name", "")) if pd.notna(row.get("feature_name")) else ""
                feature_description = str(row.get("feature_description", "")) if pd.notna(row.get("feature_description")) else ""
                
                # Call the RAG pipeline with concatenated data
                pipeline_result_json = run_rag_pipeline(feature_name + feature_description, memory)

                # Append the pipeline result to our results list
                pipeline_result = json.loads(pipeline_result_json)
                results.append(pipeline_result)
            except Exception as e:
                # If an error occurs, record it with the row index
                # logger.error(f"Error processing row {index}: {str(e)}")
                errors.append(str(e))
                errors_idx.append(index)

        # If any rows were processed successfully, create a DataFrame from the results
        if results:
            results_df = pd.DataFrame(results)
            # Ensure columns are aligned if the pipeline output varies
            results_df = results_df.reindex(columns=list(results[0].keys()))

            # Concatenate the original DataFrame with the results DataFrame
            processed_df = pd.concat([df, results_df], axis=1)
        else:
            # If no results, return the original DataFrame with a message
            processed_df = df
            # logger.warning("No rows were successfully processed.")

        # Write the new DataFrame to a BytesIO object
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            processed_df.to_excel(writer, index=False, sheet_name='Processed_Data')
            # Add a second sheet for errors if any occurred
            if errors:
                error_df = pd.DataFrame({"row_index": errors_idx, "error_message": errors})
                error_df.to_excel(writer, index=False, sheet_name='Errors')
        
        output.seek(0)
        # logger.info("Successfully created processed Excel file.")

        # Return the new Excel file as a StreamingResponse
        headers = {
            'Content-Disposition': f'attachment; filename="processed_{file.filename}"',
            'X-Errors-Count': str(len(errors))
        }

        return StreamingResponse(
            content=output, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            headers=headers
        )

    except Exception as e:
        # General error handling for the entire process
        # logger.critical(f"An unexpected error occurred during file processing: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
