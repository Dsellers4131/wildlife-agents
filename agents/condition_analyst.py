###from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
import json
import re
from dotenv import load_dotenv
from tools.scoring import calculate_condition_score


load_dotenv()

def analyze_conditions(data_package: dict) -> dict:
    
    llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv('openai_api_key'),
    temperature=0.1
)

    scoring_result = calculate_condition_score(
        data_package['weather'],
        data_package['moon']
    )

    prompt = PromptTemplate(
        input_variables = ['score', 'weather', 'moon', 'summary'],
        template="""You are an expert hunting guide explaining conditions to a hunter.

The condition score is {score}/10. Here is the factor breakdown:
{breakdown}

Current weather: {weather}
Moon phase: {moon}

Write 2 sentences explaining these conditions to a hunter in plain English.
Focus on what matters most and what they should do.
Do not mention the numerical scores.
Respond with only the 2 sentences, nothing else."""
    )

    chain = prompt | llm
    reasoning = chain.invoke({
        'score': scoring_result['score'],
        'breakdown': str(scoring_result['factor_breakdown']),
        'weather': str(data_package['weather']),
        'moon': str(data_package['moon'])
    })

    return {
        'score': scoring_result['score'],
        'should_alert': scoring_result['should_alert'],
        'reasoning': reasoning.content.strip(),
        'key_factors': [
            f"{k}: {v['score']}/{v['max']}" 
            for k, v in scoring_result['factor_breakdown'].items()
        ],
        'factor_breakdown': scoring_result['factor_breakdown']
    }

