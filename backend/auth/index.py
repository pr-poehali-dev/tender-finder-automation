import json
import os
from typing import Dict, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

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

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: User authentication and registration system
    Args: event with httpMethod, body containing telegram_id or email
          context with request_id
    Returns: HTTP response with user data and limits
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-User-Id',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    if method not in ['POST', 'GET']:
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
        conn = get_db_connection()
        cur = conn.cursor()
        
        if method == 'POST':
            body_str = event.get('body', '{}')
            if not body_str or body_str.strip() == '':
                body_str = '{}'
            body_data = json.loads(body_str)
            
            telegram_id = body_data.get('telegram_id')
            email = body_data.get('email')
            username = body_data.get('username', 'Guest')
            
            if telegram_id:
                cur.execute(
                    "SELECT * FROM users WHERE telegram_id = %s",
                    (telegram_id,)
                )
                user = cur.fetchone()
                
                if not user:
                    cur.execute(
                        "INSERT INTO users (telegram_id, username) VALUES (%s, %s) RETURNING *",
                        (telegram_id, username)
                    )
                    user = cur.fetchone()
                    conn.commit()
            elif email:
                cur.execute(
                    "SELECT * FROM users WHERE email = %s",
                    (email,)
                )
                user = cur.fetchone()
                
                if not user:
                    cur.execute(
                        "INSERT INTO users (email, username) VALUES (%s, %s) RETURNING *",
                        (email, username)
                    )
                    user = cur.fetchone()
                    conn.commit()
            else:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'telegram_id or email required'})
                }
            
            cur.close()
            conn.close()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({
                    'user': serialize_user(dict(user)),
                    'request_id': context.request_id
                })
            }
        
        if method == 'GET':
            params = event.get('queryStringParameters', {}) or {}
            user_id = params.get('user_id')
            
            if not user_id:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'user_id required'})
                }
            
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
            
            cur.close()
            conn.close()
            
            if not user:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'User not found'})
                }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({
                    'user': serialize_user(dict(user)),
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