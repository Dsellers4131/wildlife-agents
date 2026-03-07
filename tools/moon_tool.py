from datetime import datetime
import math

###load_dotenv()
### farmsense api didn't work for some reason
###calculate manually
def get_moon_phase() -> dict:

    known_new_moon = datetime(2000, 1, 6)
    now = datetime.utcnow()

    days_since = (now - known_new_moon).days
    lunar_cycle = 29.53
    position = (days_since % lunar_cycle) / lunar_cycle
    illumination = round((1 - abs(2 * position - 1)) * 100, 1)

    if position < 0.125:
        phase = 'new moon'
    elif position < 0.25:
        phase = 'waxing crescent'
    elif position < 0.375:
        phase = 'first quarter'
    elif position < 0.5:
        phase = 'waxing gibbous'
    elif position < 0.625:
        phase = 'full moon'
    elif position < 0.75:
        phase = 'waning gibbous'
    elif position < 0.875:
        phase = 'last quarter'
    else:
        phase = 'waning crescent'

    return {
        'phase': phase,
        'illumination': illumination,
        'position': round(position, 3)
    }