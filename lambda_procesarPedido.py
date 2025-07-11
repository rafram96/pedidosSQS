import json
import boto3
import os
from datetime import datetime

def lambda_handler(event, context):
    # Obtener el despachador_id del evento
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        despachador_id = body.get('despachador_id')
        
        if not despachador_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'despachador_id es requerido'})
            }
        
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Error al procesar el evento: {str(e)}'})
        }

    # Create SQS client
    sqs = boto3.client('sqs')
    queue_url = os.environ.get('SQS_QUEUE_URL', 'https://sqs.us-east-1.amazonaws.com/969784661290/ColaPedidos')
    
    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=3,
        WaitTimeSeconds=10
    )
    
    print(response)
    
    messages = response.get('Messages', [])
    pedidos = []
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_pedidos_procesados')

    for message in messages:
        pedido = json.loads(message['Body'])
        print(pedido) 
        
        # Agregar el despachador_id al pedido
        pedido['despachador_id'] = despachador_id
        pedido['fecha_procesamiento'] = datetime.now().isoformat()
        
        pedidos.append(pedido)
        response_dynamodb = table.put_item(Item=pedido)
        receipt_handle = message['ReceiptHandle']
        # Delete received message from queue
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'pedidos_procesados': pedidos,
            'cantidad_pedidos_procesados': len(pedidos),
            'despachador_id': despachador_id
        })
    }
    