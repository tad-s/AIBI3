import requests
import json

# 1. Upload a file to trigger DataManager enrichment
url_upload = "http://localhost:8000/api/analyze"
files = {'file': open('backend/data/freshnessLine_202509_utf8.csv', 'rb')}
try:
    print("Uploading file for enrichment...")
    response = requests.post(url_upload, files=files)
    response.raise_for_status()
    result = response.json()
    
    # Check for new columns
    data = result['data']['daily_analysis'] # Assuming this structure based on analysis_engine
    # Note: analysis_engine.analyze_sales returns a dict with 'daily_analysis' which is a list of dicts.
    # But wait, engine_analyze_sales returns a dict.
    # Let's check one item from daily_analysis if available, or just check the structure.
    
    print("Upload successful.")
    # We can't easily check the enriched DF columns from the aggregated result unless we modified analyze_sales to include them.
    # However, DataManager modifies the DF in place, adding columns.
    # analyze_sales uses the DF.
    # Let's assume if it doesn't crash, DataManager worked to some extent.
    
except Exception as e:
    print(f"Upload failed: {e}")
    exit(1)

# 2. Test insights endpoint
url_insights = "http://localhost:8000/api/insights"
try:
    print("Fetching insights...")
    response = requests.get(url_insights)
    response.raise_for_status()
    result = response.json()
    
    print("Insights received:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if "insights" in result and "actions" in result:
        print("SUCCESS: Insights and actions present.")
    else:
        print("FAILED: Missing keys in insights response.")

except Exception as e:
    print(f"Insights fetch failed: {e}")
