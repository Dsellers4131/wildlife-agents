from prefect import flow, task
from prefect.logging import get_run_logger
from agents.weather_collector import collect_environmental_data
from agents.condition_analyst import analyze_conditions
from tools.queue_tool import publish_alert
from tools.locations import HUNTING_LOCATIONS
from dotenv import load_dotenv
import json

load_dotenv()

MONITORED_LOCATIONS = [
    "Birmingham, AL",
    "Houston, TX"
]

@task(retries=3, retry_delay_seconds=30)###openweatherapi rerun 3 times
def fetch_conditions(location_name: str) -> dict:
    logger = get_run_logger()
    logger.info(f'fetching conditions for {location_name}')

    lat, lon = HUNTING_LOCATIONS[location_name]
    data_package = collect_environmental_data(lat, lon)

    logger.info(f'data collected for {location_name}')
    return data_package

@task(retries=2, retry_delay_seconds=15) ###running hybrid approach ollama and calcs
def score_conditions(data_package: dict, location_name: str) -> dict:
    logger = get_run_logger()
    logger.info(f'scoring conditions for {location_name}')

    result = analyze_conditions(data_package)
    logger.info(f"{location_name} scored {result['score']}/10 — alert: {result['should_alert']}")
    return result

@task ###send to aws sqs
def handle_alert(result: dict, location_name: str) -> None:
    logger = get_run_logger()
    lat, lon = HUNTING_LOCATIONS[location_name]
    location = {'name': location_name, 'lat': lat, 'lon': lon}

    if result['should_alert']:
        publish_alert(result, location)
        logger.info(f'alert sent for {location_name} ---- score {result['score']}/10')
    else:
        logger.info(f'no alert sent for {location_name} ---- score {result['score']}/10')

@flow(name='wildlife-condition-monitor', log_prints=True)
def monitoring_flow():
    logger = get_run_logger()
    logger.info(f'starting monitoring run for {len(MONITORED_LOCATIONS)} locations')

    results = {}

    for location_name in MONITORED_LOCATIONS:
        try:
            data_package = fetch_conditions(location_name)
            result = score_conditions(data_package, location_name)
            handle_alert(result, location_name)
            results[location_name] = result['score']
        except Exception as e:
            logger.error(f"Failed to process {location_name}: {e}")
            results[location_name] = "error"

    logger.info(f"Run complete. Results: {json.dumps(results)}")
    return results

# To deploy with schedule: flow.serve(name="wildlife-monitor", cron="0 */6 * * *")

if __name__ == "__main__":
    monitoring_flow()