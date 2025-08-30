from io import BytesIO
import json
import logging
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from rag_pipeline import run_rag_pipeline
from pydantic import BaseModel


app = FastAPI(title="RAG Pipeline API")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('app.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    question: str
    memory: list[str]

@app.post("/ask")
async def ask_question(request: AskRequest):
    try:
        answer = run_rag_pipeline(request.question, request.memory)
        return {"question": request.question, "answer": answer}
    except Exception as e:
        return {"error": str(e), "message": "An error occurred while processing your request."}, 500
    
@app.post("/excel")
async def upload_and_process_excel(file: UploadFile = File(...), memory: str = Form(...)):
    """
    Endpoint to upload an Excel file, process each row with the RAG pipeline,
    and return a new Excel file with the results.
    """
    logger.info(f"Received file upload: {file.filename}")
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    
    allowed_types = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only Excel files (.xlsx, .xls) are allowed.")

    try:
        # Read the uploaded Excel file into a pandas DataFrame
        excel_data = await file.read()
        df = pd.read_excel(BytesIO(excel_data))
        logger.debug(f"Successfully read Excel file with {len(df.index)} rows.")
        
        memory = json.loads(memory)
        results = []
        errors = []
        errors_idx = []

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
                logger.error(f"Error processing row {index}: {str(e)}")
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
            logger.warning("No rows were successfully processed.")

        for column in processed_df.columns:
            if processed_df[column].apply(lambda x: isinstance(x, list)).any():
                logger.info(f"Converting list data in column '{column}' to string format.")
                processed_df[column] = processed_df[column].apply(lambda x: "\n".join(x) if isinstance(x, list) else x)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            processed_df.to_excel(writer, index=False, sheet_name='Processed_Data')
            # Add a second sheet for errors if any occurred
            if errors:
                error_df = pd.DataFrame({"row_index": errors_idx, "error_message": errors})
                error_df.to_excel(writer, index=False, sheet_name='Errors')
        
        output.seek(0)
        logger.info("Successfully created processed Excel file.")

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
        logger.critical(f"An unexpected error occurred during file processing: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
