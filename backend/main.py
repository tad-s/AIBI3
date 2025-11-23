import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check API Key status
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    print(f"INFO: GOOGLE_API_KEY found: {api_key[:4]}...{api_key[-4:]}")
else:
    print("WARNING: GOOGLE_API_KEY not found in environment variables.")

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import io
import random

from analysis_engine import load_and_process_data, analyze_sales as engine_analyze_sales

from pydantic import BaseModel
from ai_agent import SalesAnalyst

app = FastAPI()

# Global variable to store the latest dataframe (MVP solution)
latest_df = None

# CORS configuration
origins = [
    "http://localhost:5173",  # Vite default port
    "http://localhost:3000",  # React default port (just in case)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    text: str

@app.post("/api/analyze")
async def analyze_sales(file: UploadFile = File(...)):
    global latest_df
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    try:
        content = await file.read()
        # Use analysis_engine to process data
        df = load_and_process_data(io.BytesIO(content))
        
        # Store for AI agent
        latest_df = df
        
        # Analyze data
        analysis_result = engine_analyze_sales(df)
        
        # Return the analysis result directly
        return {"data": analysis_result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/api/analyze_query")
async def analyze_query(request: QueryRequest):
    global latest_df
    if latest_df is None:
        raise HTTPException(status_code=400, detail="No data available. Please upload a CSV file first.")
    
    try:
        analyst = SalesAnalyst(latest_df)
        result = analyst.analyze(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Analysis failed: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Restaurant BI Backend is running (v1.2)"}
