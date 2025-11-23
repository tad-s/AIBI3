import requests
import json

# 1. Upload a file first to set the state
url_upload = "http://localhost:8000/api/analyze"
files = {'file': open('backend/data/freshnessLine_202509_utf8.csv', 'rb')}
try:
    print("Uploading file...")
    response = requests.post(url_upload, files=files)
    response.raise_for_status()
    print("Upload successful.")
except Exception as e:
    print(f"Upload failed: {e}")
    exit(1)

# 2. Test chat_analyze endpoint
url_chat = "http://localhost:8000/api/chat_analyze"
payload = {"text": "雨の日の売上傾向を教えて"}
headers = {'Content-Type': 'application/json'}

try:
    print("Sending query...")
    response = requests.post(url_chat, data=json.dumps(payload), headers=headers)
    response.raise_for_status()
    result = response.json()
    
    print("Response received:")
    print(json.dumps(result, indent=2, ensure_ascii=False)[:500] + "...")

    # Verify keys
    required_keys = ["answer", "data", "chartType", "xKey", "yKey"]
    missing_keys = [k for k in required_keys if k not in result]
    
    if missing_keys:
        print(f"FAILED: Missing keys: {missing_keys}")
    else:
        print("SUCCESS: All required keys present.")
        print(f"Chart Type: {result['chartType']}")
        print(f"xKey: {result['xKey']}")
        print(f"yKey: {result['yKey']}")

except Exception as e:
    print(f"Chat analysis failed: {e}")
