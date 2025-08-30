import json
from io import BytesIO
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from rag_pipeline import run_rag_pipeline
from pydantic import BaseModel


app = FastAPI(title="RAG Pipeline API")

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

@app.post("/upload_and_process")
async def upload_and_process_excel(file: UploadFile = File(...), memory: str = Form(...)):
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Invalid file type. Only Excel files (.xlsx, .xls) are allowed.")

        memory_list = json.loads(memory)
        df = pd.read_excel(BytesIO(await file.read()))
        
        # --- Add a check for an empty input DataFrame ---
        if df.empty:
            raise HTTPException(status_code=400, detail="The uploaded Excel file is empty.")

        results = []
        errors = []
        errors_idx = []

        for index, row in df.iterrows():
            try:
                feature_name = row.get('feature_name')
                feature_description = row.get('feature_description')
                question = feature_name + ", " + feature_description

                memory_list = json.loads(memory)

                pipeline_result = run_rag_pipeline(question, memory_list)
                results.append(json.loads(pipeline_result))
            except Exception as e:
                errors.append(str(e))
                errors_idx.append(index)
        # --- Critical: Add a check for an empty results list ---
        if not results:
            print("Warning: The 'results' list is empty. This may be due to errors in every row.")
            raise HTTPException(status_code=500, detail="Processing failed for all rows. Check the 'errors' list for details.")
            
        results_df = pd.DataFrame(results)
        # --- Ensure DataFrames have the same index for concatenation ---
        results_df.index = df.index
        processed_df = pd.concat([df, results_df], axis=1)

        for column in processed_df.columns:
            if processed_df[column].apply(lambda x: isinstance(x, list)).any():
                print(f"Converting list data in column '{column}' to string format.")
                processed_df[column] = processed_df[column].apply(lambda x: "\n".join(x) if isinstance(x, list) else x)

        output = BytesIO()

        try:
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                processed_df.to_excel(writer, index=False, sheet_name='Processed_Data')
        except Exception as e:
            print(f"Error occurred while writing to Excel: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to write processed data to Excel. This might be due to unsupported data types: {str(e)}")
        
        output.seek(0)
        
        response_content = {
            "message": "File processed successfully.",
            "errors": errors,
            "errors_idx": errors_idx,
            "file": output.getvalue().hex()
        }
        
        return response_content
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for 'memory' field.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
