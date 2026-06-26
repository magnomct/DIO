import json
import boto3
import os
from decimal import Decimal

def lambda_handler(event, context):
    # Identifica o endpoint interno do LocalStack para evitar problemas de conexão
    localstack_hostname = os.environ.get('LOCALSTACK_HOSTNAME')
    
    if localstack_hostname:
        endpoint_url = f"http://{localstack_hostname}:4566"
        s3_client = boto3.client('s3', endpoint_url=endpoint_url)
        dynamodb = boto3.resource('dynamodb', endpoint_url=endpoint_url)
    else:
        # Configuração padrão caso rode na AWS real externa
        s3_client = boto3.client('s3')
        dynamodb = boto3.resource('dynamodb')
        
    # Conecta na tabela criada no passo anterior
    table = dynamodb.Table('NotasFiscais')
    
    # Mapeia e processa o evento disparado pelo S3
    for record in event.get('Records', []):
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        
        print(f"Arquivo detectado no S3: {object_key} (Bucket: {bucket_name})")
        
        try:
            # 1. Baixa o arquivo JSON do S3 local
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            file_content = response['Body'].read().decode('utf-8')
            
            # 2. Converte o texto do arquivo para uma lista Python
            notas_fiscais = json.loads(file_content)
            
            # 3. Itera sobre as 10 linhas do JSON e envia para o DynamoDB
            for nota in notas_fiscais:
                print(f"Gravando nota fiscal no DynamoDB: {nota['id']}")
                
                table.put_item(
                    Item={
                        'id': nota['id'],                         # Chave primária (String)
                        'cliente': nota['cliente'],               # Atributo (String)
                        'valor_total': Decimal(str(nota['valor_total'])), # Convertido para evitar erro de Float
                        'data_emissao': nota['data_emissao']       # Atributo (String)
                    }
                )
                
            print("Todas as notas fiscais foram processadas com sucesso!")
            
        except Exception as e:
            print(f"Erro ao processar o arquivo {object_key}: {str(e)}")
            raise e
            
    return {
        'statusCode': 200,
        'body': json.dumps('Processamento concluído com sucesso!')
    }