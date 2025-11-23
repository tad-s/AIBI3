import pandas as pd
import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from analysis_engine import load_and_process_data, analyze_sales

file_path = r'c:\Users\tarchi\Desktop\HTS\AIBI3\backend\data\freshnessLine_202509_utf8.csv'

print(f"Testing with file: {file_path}")

try:
    print("Loading and processing data...")
    df = load_and_process_data(file_path)
    print("Data loaded successfully.")
    print(df.head())
    print(df.columns)
    
    print("Analyzing sales...")
    result = analyze_sales(df)
    print("Analysis successful.")
    print(result.keys())

except Exception as e:
    print("Error occurred:")
    print(e)
    import traceback
    traceback.print_exc()
