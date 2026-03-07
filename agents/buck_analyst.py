from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from data.buck_profiles import get_buck_sightings, BUCK_PROFILES
from tools.scoring import calculate_condition_score
import os
from dotenv import load_dotenv

load_dotenv()

def analyze_buck_opportunity(buck_name: str, weather: dict, moon: dict) -> dict:
    """
    Agentic reasoning engine.
    Combines live conditions with buck sighting history
    to produce a hunting recommendation.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv('openai_api_key'),
        temperature=0.3
    )

    # Get buck profile and history
    profile = BUCK_PROFILES[buck_name]
    sightings = get_buck_sightings(buck_name)

    # Score current conditions
    scoring = calculate_condition_score(weather, moon)

    # Find similar historical conditions from sighting history
    similar_sightings = []
    for s in sightings:
        temp_match = abs(s['temperature'] - weather['temperature']) < 15
        wind_match = abs(s['wind_speed'] - weather['wind_speed']) < 8
        if temp_match and wind_match:
            similar_sightings.append(s)

    # Last sighting
    last_sighting = sightings[-1] if sightings else None

    prompt = PromptTemplate(
        input_variables=[
            'buck_name', 'profile', 'condition_score',
            'weather', 'moon', 'sightings',
            'similar_sightings', 'last_sighting'
        ],
        template="""You are an elite hunting guide with 20 years of experience 
reading deer behavior and pattern data. You have access to trail camera history 
and live conditions.

BUCK PROFILE:
Name: {buck_name}
{profile}

CURRENT CONDITIONS:
{weather}
Moon: {moon}
Condition Score: {condition_score}/10

SIGHTING HISTORY (last 30 days):
Total sightings: {sightings}

SIMILAR CONDITION SIGHTINGS (conditions close to today):
{similar_sightings}

LAST CONFIRMED SIGHTING:
{last_sighting}

Based on this buck's pattern history and today's live conditions, write a 
hunting recommendation for this hunter. Be specific — mention the buck by name, 
reference his patterns, give a specific recommended action and time.

Write exactly 3 sentences. Sound like a seasoned guide talking to a hunter, 
not a data report. Be direct and confident. End with a specific recommended action."""
    )

    chain = prompt | llm

    reasoning = chain.invoke({
        'buck_name': buck_name,
        'profile': str(profile),
        'condition_score': scoring['score'],
        'weather': str(weather),
        'moon': str(moon),
        'sightings': len(sightings),
        'similar_sightings': str(similar_sightings[-3:]) if similar_sightings else "No similar conditions found",
        'last_sighting': str(last_sighting)
    })

    # Determine urgency
    score = scoring['score']
    similar_count = len(similar_sightings)

    if score >= 7 and similar_count >= 3:
        urgency = "HIGH"
        urgency_color = "#f5a623"
    elif score >= 5 and similar_count >= 1:
        urgency = "MODERATE"
        urgency_color = "#4a7c2f"
    else:
        urgency = "LOW"
        urgency_color = "#7a7568"

    return {
        'buck_name': buck_name,
        'profile': profile,
        'recommendation': reasoning.content.strip(),
        'urgency': urgency,
        'urgency_color': urgency_color,
        'condition_score': score,
        'similar_sightings_count': similar_count,
        'total_sightings': len(sightings),
        'last_sighting': last_sighting,
        'factor_breakdown': scoring['factor_breakdown']
    }