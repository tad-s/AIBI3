import requests

# 1. Upload a file first (required for PDF generation)
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

# 2. Test PDF generation
url_pdf = "http://localhost:8000/api/generate_pdf"
try:
    print("Generating PDF...")
    response = requests.post(url_pdf)
    response.raise_for_status()
    
    # Check content type
    content_type = response.headers.get('Content-Type')
    print(f"Content-Type: {content_type}")
    
    if 'application/pdf' in content_type:
        print("SUCCESS: PDF generated.")
        # Save to file to inspect manually if needed
        with open('test_report.pdf', 'wb') as f:
            f.write(response.content)
        print("Saved to test_report.pdf")
    else:
        print(f"FAILED: Unexpected content type: {content_type}")

except Exception as e:
    print(f"PDF generation failed: {e}")
