from datetime import datetime, timedelta
import random

def generate_ghost_sightings():
    """
    Ghost — nocturnal, pressured buck, moves during cold fronts.
    Rarely shows in daylight. When he does it's special.
    """
    sightings = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        date = base_date + timedelta(days=i)
        
        # Ghost appears every 3-4 days
        if i % 3 != 0:
            continue
            
        # Ghost moves at night or very early morning
        hour = random.choice([5, 6, 19, 20, 21, 22])
        
        # Ghost likes cold temps and rising pressure
        temp = random.uniform(38, 58)
        pressure = random.uniform(1015, 1025)
        wind = random.uniform(2, 8)
        moon_phases = ["New Moon", "Waxing Crescent", "Last Quarter"]
        moon = random.choice(moon_phases)
        
        sightings.append({
            "buck": "Ghost",
            "date": date.strftime("%Y-%m-%d"),
            "hour": hour,
            "time_of_day": "Dawn" if hour < 8 else "Dusk" if hour > 17 else "Midday",
            "temperature": round(temp, 1),
            "pressure": round(pressure, 1),
            "wind_speed": round(wind, 1),
            "moon_phase": moon,
            "location": "East Ridge Trail",
            "notes": "Nocturnal pattern — cold front mover"
        })
    
    return sightings


def generate_wide_load_sightings():
    """
    Wide Load — predictable, dominant buck. Shows every 2-3 days
    at the morning feeder. Creature of habit.
    """
    sightings = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        date = base_date + timedelta(days=i)
        
        # Wide Load appears every 2 days like clockwork
        if i % 2 != 0:
            continue
        
        # Wide Load is a morning feeder buck
        hour = random.choice([6, 7, 8, 9])
        
        # Wide Load doesn't care much about conditions — he's dominant
        temp = random.uniform(45, 75)
        pressure = random.uniform(1005, 1025)
        wind = random.uniform(0, 15)
        moon_phases = ["New Moon", "Waxing Crescent", "First Quarter",
                       "Full Moon", "Last Quarter", "Waning Crescent"]
        moon = random.choice(moon_phases)
        
        sightings.append({
            "buck": "Wide Load",
            "date": date.strftime("%Y-%m-%d"),
            "hour": hour,
            "time_of_day": "Dawn",
            "temperature": round(temp, 1),
            "pressure": round(pressure, 1),
            "wind_speed": round(wind, 1),
            "moon_phase": moon,
            "location": "North Feeder",
            "notes": "Morning feeder — highly predictable"
        })
    
    return sightings


def generate_timber_sightings():
    """
    Timber — pressured, skittish buck. Only moves on calm low-wind days.
    Unpredictable timing but wind is always the key factor.
    """
    sightings = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        date = base_date + timedelta(days=i)
        
        # Timber is unpredictable — appears randomly
        if random.random() > 0.4:
            continue
        
        # Timber moves morning or evening but never midday
        hour = random.choice([6, 7, 17, 18, 19])
        
        # Timber only moves when wind is very low
        wind = random.uniform(0, 6)
        temp = random.uniform(42, 68)
        pressure = random.uniform(1008, 1022)
        moon_phases = ["New Moon", "Waxing Crescent", "First Quarter", "Last Quarter"]
        moon = random.choice(moon_phases)
        
        sightings.append({
            "buck": "Timber",
            "date": date.strftime("%Y-%m-%d"),
            "hour": hour,
            "time_of_day": "Dawn" if hour < 12 else "Dusk",
            "temperature": round(temp, 1),
            "pressure": round(pressure, 1),
            "wind_speed": round(wind, 1),
            "moon_phase": moon,
            "location": "South Thicket",
            "notes": "Wind-sensitive — spooks at 10mph+"
        })
    
    return sightings


def get_all_sightings():
    """Returns combined sighting history for all three bucks."""
    return (
        generate_ghost_sightings() +
        generate_wide_load_sightings() +
        generate_timber_sightings()
    )


def get_buck_sightings(buck_name: str):
    """Returns sighting history for a specific buck."""
    all_sightings = get_all_sightings()
    return [s for s in all_sightings if s["buck"] == buck_name]


BUCK_PROFILES = {
    "Ghost": {
        "name": "Ghost",
        "nickname": "The Nocturnal Giant",
        "estimated_age": "5-6 years",
        "estimated_score": "158 B&C",
        "personality": "Nocturnal, pressured, moves only during cold fronts",
        "key_trigger": "Cold front + rising pressure + low wind",
        "best_stand": "East Ridge Trail",
        "best_time": "First light or last light only",
        "caution": "Any human pressure shuts him down for days"
    },
    "Wide Load": {
        "name": "Wide Load",
        "nickname": "The Feeder King",
        "estimated_age": "4-5 years",
        "estimated_score": "142 B&C",
        "personality": "Dominant, predictable, creature of habit",
        "key_trigger": "Morning — shows up regardless of conditions",
        "best_stand": "North Feeder",
        "best_time": "6-9am daily",
        "caution": "Pattern breaks during peak rut — he roams"
    },
    "Timber": {
        "name": "Timber",
        "nickname": "The Ghost of the Thicket",
        "estimated_age": "3-4 years",
        "estimated_score": "128 B&C",
        "personality": "Skittish, pressured, wind-sensitive",
        "key_trigger": "Calm wind under 6mph — non-negotiable",
        "best_stand": "South Thicket",
        "best_time": "Unpredictable — but always calm wind",
        "caution": "Any wind over 10mph and he disappears"
    }
}