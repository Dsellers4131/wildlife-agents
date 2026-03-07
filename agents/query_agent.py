from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from data.buck_profiles import get_all_sightings, BUCK_PROFILES
import os
from dotenv import load_dotenv

load_dotenv()

def query_buck_data(question: str) -> str:
    """
    Natural language query agent.
    Hunter asks a question in plain English,
    agent reasons over sighting data and returns a conversational answer.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv('openai_api_key'),
        temperature=0.2
    )

    all_sightings = get_all_sightings()

    prompt = PromptTemplate(
        input_variables=['question', 'sightings', 'profiles'],
        template="""You are an expert hunting data analyst with access to 
30 days of trail camera sighting data for three bucks.

BUCK PROFILES:
{profiles}

SIGHTING DATA (last 30 days):
{sightings}

HUNTER'S QUESTION:
{question}

Answer the hunter's question directly and conversationally using the sighting data.
Be specific — reference actual patterns, times, conditions from the data.
If the data doesn't support a clear answer, say so honestly.
Keep your answer to 2-3 sentences maximum.
Sound like a knowledgeable guide, not a data report."""
    )

    chain = prompt | llm

    response = chain.invoke({
        'question': question,
        'sightings': str(all_sightings),
        'profiles': str(BUCK_PROFILES)
    })

    return response.content.strip()