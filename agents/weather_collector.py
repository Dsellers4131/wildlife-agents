from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from tools.weather_tool import get_weather_conditions
from tools.moon_tool import get_moon_phase
import os
from dotenv import load_dotenv

load_dotenv()

def collect_environmental_data(lat: float, lon: float) -> dict:
    llm = OllamaLLM(
        model = os.getenv('ollama_model', 'llama3.1:8b'),
        base_url = os.getenv('ollama_base_url', 'http://localhost:11434'),
        temperature = 0.1 ### - may want to increase this slightly will review after testing
    )

    weather = get_weather_conditions(lat, lon)
    moon = get_moon_phase()

    data_package = {
        'weather': weather,
        'moon': moon,
        'location': {'lat': lat, 'lon': lon}
    }

    

    prompt = PromptTemplate(
        input_variables = ['weather', 'moon'],
        template = """
        You are a wildlife data compiler. Your job is to summarize
        environmental conditions clearly and concisely for a 
        hunting condition analysts.

        Current weather conditions: {weather}
        Current moon phase: {moon}

        Provide a clean, structured 2-3 sentence summary of these conditions.
        Focus on the factors most relevant to deer movement."""
    )

    chain = prompt | llm
    summary = chain.invoke({
        'weather': str(weather),
        'moon': str(moon)
    })

    data_package['summary'] = summary
    return data_package