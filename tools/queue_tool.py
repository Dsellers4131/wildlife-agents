import boto3
import json 
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def publish_alert(condition_result: dict, location: dict) -> dict:

    sqs = boto3.client(
        'sqs',
        region_name = os.getenv('aws_region'),
        aws_access_key_id = os.getenv('aws_access_key_id'),
        aws_secret_access_key = os.getenv('aws_secret_access_key')
    )

    message = {
        'alert_type': "HIGH_ACTIVITY_CONDITIONS",
        'score': condition_result['score'],
        'reasoning': condition_result['reasoning'],
        'key_factors': condition_result['key_factors'],
        'location': location,
        'timestamp': datetime.utcnow().isoformat()
    }

    response = sqs.send_message(
        QueueUrl = os.getenv('sqs_queue_url'),
        MessageBody = json.dumps(message)
    )

    print(f'alert published - message id: {response['MessageId']}')
    return response