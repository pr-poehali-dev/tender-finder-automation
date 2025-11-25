import json
import os
from typing import Dict, Any

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: Generate code using OpenAI API based on user prompt
    Args: event with httpMethod, body containing prompt
          context with request_id
    Returns: HTTP response with generated code
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-User-Id',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        body_str = event.get('body', '{}')
        if not body_str or body_str.strip() == '':
            body_str = '{}'
        body_data = json.loads(body_str)
        prompt = body_data.get('prompt', '')
        
        if not prompt:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({'error': 'Prompt is required'})
            }
        
        openai_key = os.environ.get('OPENAI_API_KEY')
        if not openai_key:
            generated_code = f"""# Код сгенерирован на основе запроса: {prompt}

def example_function():
    # Реализация функции
    return 'Результат'
"""
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({
                    'code': generated_code,
                    'request_id': context.request_id,
                    'mock': True
                })
            }
        
        import openai
        openai.api_key = openai_key
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Ты - опытный программист. Генерируй чистый, хорошо структурированный код с комментариями на русском языке."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        generated_code = response.choices[0].message.content
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'isBase64Encoded': False,
            'body': json.dumps({
                'code': generated_code,
                'request_id': context.request_id
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'isBase64Encoded': False,
            'body': json.dumps({'error': str(e)})
        }