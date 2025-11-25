import json
import os
from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

def serialize_datetime(obj):
    '''Convert datetime objects to ISO format strings'''
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def serialize_user(user_dict):
    '''Serialize user dict with datetime conversion'''
    return {k: serialize_datetime(v) for k, v in user_dict.items()}

def get_db_connection():
    '''Get database connection using DATABASE_URL'''
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError('DATABASE_URL not configured')
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)

def send_telegram_message(chat_id: int, text: str, bot_token: str):
    '''Send message via Telegram Bot API'''
    import requests
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: Telegram bot webhook handler for code generation
    Args: event with httpMethod, body containing Telegram update
          context with request_id
    Returns: HTTP response confirming webhook processing
    '''
    method: str = event.get('httpMethod', 'POST')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
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
            'isBase64Encoded': False,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'isBase64Encoded': False,
                'body': json.dumps({'ok': True, 'message': 'Bot token not configured'})
            }
        
        body_str = event.get('body', '{}')
        if not body_str or body_str.strip() == '':
            body_str = '{}'
        update = json.loads(body_str)
        
        if 'message' not in update:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'isBase64Encoded': False,
                'body': json.dumps({'ok': True})
            }
        
        message = update['message']
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        username = message['from'].get('username', 'User')
        text = message.get('text', '')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM users WHERE telegram_id = %s", (user_id,))
        user = cur.fetchone()
        
        if not user:
            cur.execute(
                "INSERT INTO users (telegram_id, username) VALUES (%s, %s) RETURNING *",
                (user_id, username)
            )
            user = cur.fetchone()
            conn.commit()
            
            welcome_msg = f"Привет, {username}! 🚀\n\nЯ помогу генерировать код с помощью ИИ.\n\nУ тебя есть {user['free_requests_limit']} бесплатных запросов.\n\nПросто отправь описание задачи!"
            send_telegram_message(chat_id, welcome_msg, bot_token)
        
        elif text.startswith('/start'):
            info_msg = f"Привет, {username}! 👋\n\nИспользовано запросов: {user['free_requests_used']}/{user['free_requests_limit']}\nСтатус: {'Premium 💎' if user['is_premium'] else 'Free'}\n\nОтправь описание задачи для генерации кода!"
            send_telegram_message(chat_id, info_msg, bot_token)
        
        else:
            if not user['is_premium'] and user['free_requests_used'] >= user['free_requests_limit']:
                limit_msg = "⚠️ Лимит бесплатных запросов исчерпан!\n\nПерейдите на Premium для безлимитной генерации кода."
                send_telegram_message(chat_id, limit_msg, bot_token)
            else:
                openai_key = os.environ.get('OPENAI_API_KEY')
                
                if openai_key:
                    import openai
                    openai.api_key = openai_key
                    
                    response = openai.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Ты опытный программист. Генерируй код с комментариями на русском."},
                            {"role": "user", "content": text}
                        ],
                        temperature=0.7,
                        max_tokens=1500
                    )
                    
                    generated_code = response.choices[0].message.content
                else:
                    generated_code = f"```python\n# Код для: {text}\ndef example():\n    return 'Результат'\n```"
                
                cur.execute(
                    "INSERT INTO usage_history (user_id, prompt, generated_code) VALUES (%s, %s, %s)",
                    (user['id'], text, generated_code)
                )
                
                if not user['is_premium']:
                    cur.execute(
                        "UPDATE users SET free_requests_used = free_requests_used + 1 WHERE id = %s",
                        (user['id'],)
                    )
                
                conn.commit()
                
                send_telegram_message(chat_id, f"✅ Код сгенерирован:\n\n{generated_code}", bot_token)
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'isBase64Encoded': False,
            'body': json.dumps({'ok': True})
        }
        
    except Exception as e:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'isBase64Encoded': False,
            'body': json.dumps({'ok': True, 'error': str(e)})
        }
