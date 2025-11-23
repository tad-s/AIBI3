import pandas as pd
import google.generativeai as genai
import os
import io

class SalesAnalyst:
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with the sales DataFrame.
        """
        self.df = df
        
        # Configure Gemini API
        # Note: API key should be set in environment variable GOOGLE_API_KEY
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("Warning: GOOGLE_API_KEY environment variable not found.")
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')

    def analyze(self, query: str) -> dict:
        """
        Analyze the dataframe based on the natural language query.
        """
        if not hasattr(self, 'model'):
             return {"error": "Gemini API not configured. Please set GOOGLE_API_KEY."}

        # Capture dataframe info
        buffer = io.StringIO()
        self.df.info(buf=buffer)
        df_info = buffer.getvalue()

        # Construct the prompt
        prompt = f"""
        You are a Python Data Analyst. You are given a pandas DataFrame named `df` with the following structure:
        
        {df_info}
        
        The user asks: "{query}"
        
        Please write Python code to analyze `df` and answer the question.
        
        Requirements:
        1. The code must be valid Python.
        2. Do NOT read any files. Use the existing `df` variable.
        3. The code MUST create a variable named `result_data`.
           - `result_data` should be a list of dictionaries (records) representing the aggregated data, suitable for JSON serialization.
           - Example: `[{{"date": "2025-09-01", "sales": 1000}}, ...]`
        4. The code MUST create a variable named `chart_type`.
           - `chart_type` should be one of: 'bar', 'line', 'pie', 'scatter', 'table'.
        5. The code MUST create a variable named `x_key` (string) indicating the key for the X-axis (or label).
        6. The code MUST create a variable named `y_key` (string) indicating the key for the Y-axis (or value).
        7. The code MUST create a variable named `summary` (string).
           - Provide a brief summary of the analysis results in Japanese.
        8. Return ONLY the Python code. Do not include markdown backticks (```) or explanations.
        
        Code:
        """

        try:
            # Generate code
            response = self.model.generate_content(prompt)
            generated_code = response.text.strip()
            
            # Clean up markdown if present
            if generated_code.startswith("```python"):
                generated_code = generated_code.replace("```python", "").replace("```", "")
            elif generated_code.startswith("```"):
                generated_code = generated_code.replace("```", "")
            
            print(f"Generated Code:\n{generated_code}")

            # Execute code
            local_vars = {'df': self.df, 'pd': pd}
            exec(generated_code, {}, local_vars)
            
            result_data = local_vars.get('result_data')
            chart_type = local_vars.get('chart_type', 'bar')
            x_key = local_vars.get('x_key', '')
            y_key = local_vars.get('y_key', '')
            summary = local_vars.get('summary', '分析が完了しました。')
            
            if result_data is None:
                return {"error": "The generated code did not produce 'result_data'."}
                
            return {
                "type": chart_type,
                "data": result_data,
                "x_key": x_key,
                "y_key": y_key,
                "summary": summary,
                "generated_code": generated_code
            }

        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
