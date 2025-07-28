import requests

def explain_query(api_key, query):
    """Explain SQL query in simple terms"""
    if not api_key:
        return "Google API key is missing"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    prompt = f"""
    Explain this SQL query in simple terms:
    1. What does the query do?
    2. Which tables/columns are involved?
    3. Describe any conditions
    
    Query:
    {query}
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        response_json = response.json()
        
        if 'candidates' in response_json and response_json['candidates']:
            return response_json['candidates'][0]['content']['parts'][0]['text']
        return "Failed to generate explanation"
    except Exception as e:
        return f"Explanation error: {str(e)}"