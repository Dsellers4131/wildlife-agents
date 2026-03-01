from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

def analyze_conditions(data_package: dict) -> dict:
    
    llm = OllamaLLM(
        model = os.getenv('ollama_model', 'llama3.1:8b'),
        base_url = os.getenv('ollama_base_url', 'http://localhost:11434'),
        temperature = 0.1
    )

    prompt = PromptTemplate(
        input_variables = ['weather', 'moon', 'summary'],
        template ="""You are an expert wildlife biologist and hunting guide.
        Analyze these conditions and score deer movement likelihood. 
        
        Weather: {weather}
        Moon phase: {moon}
        Analysis Summary: {summary}
        
        Scoring criteria:
        - Barometric pressure 1010-1020 hPa = ideal
        - Temp 35-65F = ideal, above 75F = poor
        - Wind speed under 15mph = good, over 25mph = poor
        - Last quarter or New moon = moderate activity
        - Full moon = high nocturnal activity, low daytime activity
        
        You must respond with ONLY a JSON object. No explanation, no markdown, no backticks.
        Respond exactly like this example:
        {{"score": 7, "should_alert": true, "reasoning": "your reasoning here", "key_factors": ["factor1", "factor2"]}}"""
    )

    chain = prompt | llm
    response = chain.invoke({
        'weather': str(data_package['weather']),
        'moon': str(data_package['moon']),
        'summary': str(data_package.get('summary', ''))
    })

    cleaned = response.strip()
    cleaned = re.sub(r'```json|```', '', cleaned).strip() # post processing ensure response is json
    
    match = re.search(r'\{.*\}', cleaned, re.DOTALL) # extracts only json more post processing
    if not match:
        raise ValueError(f'no json found in response: {cleaned}')
    
    result = json.loads(match.group())

    required_fields = ['score', 'should_alert', 'reasoning', 'key_factors']
    for field in required_fields:
        if field not in result:
            raise ValueError(f'missing required field: {field}')
        
    return result