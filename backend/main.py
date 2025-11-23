import os
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv() # Fallback to default

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
    text: str | None = None
    query: str | None = None

@app.post("/api/analyze")
async def analyze_sales(file: UploadFile = File(...)):
    global latest_df
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    try:
        content = await file.read()
        # Use DataManager to process data
        from data_manager import DataManager
        dm = DataManager()
        df = dm.get_enriched_data(io.BytesIO(content))
        
        # Store for AI agent
        latest_df = df
        
        # Analyze data (using existing engine for basic stats)
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
        # Use the new LLMAnalyst from analysis_engine
        from analysis_engine import LLMAnalyst
        analyst = LLMAnalyst()
        result = analyst.analyze_query(latest_df, request.text)
        
        # For backward compatibility
        from ai_agent import SalesAnalyst
        analyst_old = SalesAnalyst(latest_df)
        return analyst_old.analyze(request.text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Analysis failed: {str(e)}")

@app.post("/api/chat_analyze")
async def chat_analyze(request: QueryRequest):
    global latest_df
    if latest_df is None:
        raise HTTPException(status_code=400, detail="No data available. Please upload a CSV file first.")
    
    try:
        from analysis_engine import LLMAnalyst
        analyst = LLMAnalyst()
        user_query = request.query if request.query else request.text
        if not user_query:
            raise HTTPException(status_code=400, detail="Query text is required.")
            
        result = analyst.analyze_query(latest_df, user_query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Analysis failed: {str(e)}")

@app.get("/api/insights")
async def get_insights():
    global latest_df
    if latest_df is None:
        raise HTTPException(status_code=400, detail="No data available. Please upload a CSV file first.")
    
    try:
        from insight_engine import InsightEngine
        engine = InsightEngine()
        result = engine.generate_proactive_insights(latest_df)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {str(e)}")

from fastapi.responses import StreamingResponse

@app.post("/api/generate_pdf")
async def generate_pdf():
    global latest_df
    if latest_df is None:
        raise HTTPException(status_code=400, detail="No data available. Please upload a CSV file first.")
    
    try:
        # 1. Generate Insights first
        from insight_engine import InsightEngine
        insight_engine = InsightEngine()
        insights_data = insight_engine.generate_proactive_insights(latest_df)
        
        # 2. Generate PDF
        from pdf_generator import PDFGenerator
        pdf_gen = PDFGenerator()
        pdf_buffer = pdf_gen.generate_report(latest_df, insights_data)
        
        return StreamingResponse(
            pdf_buffer, 
            media_type="application/pdf", 
            headers={"Content-Disposition": "attachment; filename=report.pdf"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Restaurant BI Backend is running (v1.4)"}
