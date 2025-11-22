import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import io
import random

app = FastAPI()

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

# Mock data constants
WEATHER_CONDITIONS = ["Sunny", "Rainy", "Cloudy"]
EVENTS = ["Local Festival", "Concert", "Sports Match", "None"]
TRENDS = ["#Pancakes", "#SpicyFood", "#Healthy", "#Tapioca", "None"]

def generate_mock_data(num_rows):
    """Generates mock data for weather, events, and trends."""
    weather_data = []
    event_data = []
    trend_data = []

    for _ in range(num_rows):
        # Weather: Condition + Random Temperature (15-30)
        condition = random.choice(WEATHER_CONDITIONS)
        temp = random.randint(15, 30)
        weather_data.append(f"{condition} ({temp}C)")
        
        # Event and Trend
        event_data.append(random.choice(EVENTS))
        trend_data.append(random.choice(TRENDS))
    
    return weather_data, event_data, trend_data

@app.post("/api/analyze")
async def analyze_sales(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        # Generate mock data matching the number of rows in the CSV
        weather, events, trends = generate_mock_data(len(df))
        
        # Append mock data to DataFrame
        df['Weather'] = weather
        df['Event'] = events
        df['Trend'] = trends
        
        # Convert to JSON compatible format (list of dicts)
        result = df.to_dict(orient='records')
        
        return {"data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Restaurant BI Backend is running"}
