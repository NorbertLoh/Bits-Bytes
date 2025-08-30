# Bits-Bytes

# Backend
Setup instructions for the backend server using FastAPI and Uvicorn.
1. Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
    
    On Windows use:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```
2. Install the required packages in the virtual environment:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the FastAPI server:
    ```bash
    uvicorn api.main:app --host 0.0.0.0 --port 8000
    ```

# Frontend
Setup instructions for the frontend using React.
1. Navigate to the frontend directory and install dependencies:
    ```bash
    cd frontend
    npm install
    ```
2. Start the development server:
    ```bash
    npm start
    ```

# Fine-tuning
Instructions for fine-tuning the model using the provided dataset.
1. Navigate to the fine-tuning directory:
    ```bash
    cd fine_tuning
    ```
2. Axolotl requires linux or WSL2 on Windows. Ensure you have the necessary environment set up.
3. Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
4. Install the required packages in the virtual environment:
    ```bash
    pip install -r requirements.txt
    ```
5. Run the notebook:
    ```bash
    jupyter notebook
    ```

# Running Trained GGUF Model
Instructions for running the trained GGUF model using Ollama.
1. Load model into Ollama:
    ```bash
    cd finetuning
    ollama create <model-name> -f Modelfile
    ```
2. Run the model:
    ```bash
    ollama serve
    ```