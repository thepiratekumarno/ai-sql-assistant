import re
import requests
from src.database.schema import get_table_columns

def generate_sql_query(api_key, user_prompt, credentials, database, table_name):
    """Generate SQL query from natural language with improved prompt"""
    if not api_key:
        return {"error": "Google API key is missing"}
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    # Get table columns
    columns = get_table_columns(credentials, database, table_name)
    schema_prompt = f"Columns: {', '.join(columns)}" if columns else "No schema information available"
    
    prompt = f"""
    You are an expert SQL developer. Convert this natural language command into a valid MySQL query.
    Database: {database}
    Table: {table_name}
    
    Table Structure:
    {schema_prompt}
    
    Critical Guidelines:
    1. Always use backticks around table/column names
    2. For INSERT: Include all required columns and values
    3. For UPDATE: Always include a WHERE clause
    4. For DATE/DATETIME: Use proper formatting (YYYY-MM-DD HH:MM:SS)
    5. Return ONLY the SQL query without any explanations
    
    Examples:
    Command: "Add new student: John, age 22"
    INSERT INTO `students` (`name`, `age`) VALUES ('John', 22)
    
    Command: "Update name harsh to manish"
    UPDATE `students` SET `name` = 'manish' WHERE `name` = 'harsh'
    
    Command: "{user_prompt}"
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1000,
            "topP": 0.8,
            "topK": 40
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        response_json = response.json()
        
        # Extract text response
        if 'candidates' in response_json and response_json['candidates']:
            query_text = response_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return {"error": "Unexpected API response"}
        
        # Clean up the response
        query_text = re.sub(r'^```sql|```$', '', query_text, flags=re.IGNORECASE).strip()
        return query_text
    except Exception as e:
        return {"error": f"Error generating SQL: {str(e)}"}