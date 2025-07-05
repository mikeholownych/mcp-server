import os
import requests

def send_slack_notification(message: str):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        raise ValueError("The SLACK_WEBHOOK_URL environment variable is not set.")
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    data = {
        "text": message
    }
    
    response = requests.post(webhook_url, json=data, headers=headers)
    
    if response.status_code != 200:
        raise ValueError(
            f'Request to Slack returned an error {response.status_code}, the response is:\n{response.text}'
        )


def notify_test_failure(test_name: str):
    message = f":x: Test Failed: {test_name}"
    send_slack_notification(message)


def notify_deployment(environment: str):
    message = f":rocket: Deployment to {environment} succeeded."
    send_slack_notification(message)


def notify_rollback(environment: str):
    message = f":rewind: Rollback executed on {environment}."
    send_slack_notification(message)
