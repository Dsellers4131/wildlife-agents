### manually scoring because llm had different scores even if i ran same city 2 secs later
### manually scoring will help be more accurate a ML model with historical data would 
### help even more 

def score_pressure(pressure_hpa: float) -> tuple[int, str]:
    if 1010 <= pressure_hpa <= 1020:
        return 3, 'ideal stable pressure'
    elif 1000 <= pressure_hpa < 1010 or 1020 < pressure_hpa <= 1030:
        return 2, 'slightly off ideal pressure'
    else:
        return 1, 'extremem pressure - deer bedded down'
    
def score_temperature(temp_f: float) -> tuple[int, str]:
    if 35 <= temp_f <= 55:
        return 3, "peak movement temperature range"
    elif 55 < temp_f <= 65:
        return 2, "slightly warm but acceptable"
    elif 65 < temp_f <= 75:
        return 1, "warm reduced deer movement expected"
    else:
        return 0, "too hot deer will be bedded"


def score_wind(wind_mph: float) -> tuple[int, str]:
    if wind_mph < 10:
        return 2, "calm wind deer feel secure"
    elif 10 <= wind_mph <= 20:
        return 1, "moderate wind cautious movement"
    else:
        return 0, "high wind deer won't move"


def score_moon(phase: str) -> tuple[int, str]:
    phase = phase.lower()
    if "new" in phase:
        return 2, "new moon, peak daytime movement"
    elif "quarter" in phase or "crescent" in phase:
        return 1, "moderate moon phase"
    elif "full" in phase:
        return 0, "full moon, deer active overnight, bedded now"
    else:
        return 1, "unknown moon phase, moderate assumed"
    
def calculate_condition_score(weather: dict, moon: dict) -> dict:
    pressure_score, pressure_reason = score_pressure(weather["pressure"])
    temp_score, temp_reason = score_temperature(weather["temperature"])
    wind_score, wind_reason = score_wind(weather["wind_speed"])
    moon_score, moon_reason = score_moon(moon["phase"])

    total = pressure_score + temp_score + wind_score + moon_score

    # Should alert threshold
    should_alert = total >= 7

    return {
        "score": total,
        "should_alert": should_alert,
        "factor_breakdown": {
            "pressure": {"score": pressure_score, "max": 3, "reason": pressure_reason},
            "temperature": {"score": temp_score, "max": 3, "reason": temp_reason},
            "wind": {"score": wind_score, "max": 2, "reason": wind_reason},
            "moon": {"score": moon_score, "max": 2, "reason": moon_reason}
        }
    }