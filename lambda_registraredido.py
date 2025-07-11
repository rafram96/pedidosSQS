import json
import boto3
import os

def lambda_handler(event, context):
    pedido = json.dumps(event)

    # Create SQS client
    sqs = boto3.client('sqs')
    queue_url = os.environ.get('SQS_QUEUE_URL', 'https://sqs.us-east-1.amazonaws.com/969784661290/ColaPedidos')

    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=(pedido)
    )

    # Salida (json)
    return {
        'statusCode': 200,
        'respuesta': response
    }