import json
import os
from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    '''Get database connection using DATABASE_URL'''
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError('DATABASE_URL not configured')
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: Create Stripe payment session for premium upgrade
    Args: event with httpMethod, body containing user_id
          context with request_id
    Returns: HTTP response with payment URL or confirmation
    '''
    method: str = event.get('httpMethod', 'POST')
    
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
            'isBase64Encoded': False,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        stripe_key = os.environ.get('STRIPE_SECRET_KEY')
        
        body_str = event.get('body', '{}')
        if not body_str or body_str.strip() == '':
            body_str = '{}'
        body_data = json.loads(body_str)
        
        user_id = body_data.get('user_id')
        action = body_data.get('action', 'create_session')
        
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
        
        if action == 'upgrade_to_premium':
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute(
                "UPDATE users SET is_premium = TRUE WHERE id = %s RETURNING *",
                (user_id,)
            )
            user = cur.fetchone()
            conn.commit()
            
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
                    'success': True,
                    'message': 'User upgraded to premium',
                    'user_id': user_id
                })
            }
        
        if not stripe_key:
            payment_url = f"https://example.com/payment?user_id={user_id}"
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({
                    'payment_url': payment_url,
                    'mock': True,
                    'message': 'Stripe not configured, using mock URL'
                })
            }
        
        import stripe
        stripe.api_key = stripe_key
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Premium Plan',
                        'description': 'Безлимитная генерация кода с ИИ',
                    },
                    'unit_amount': 999,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'https://yourapp.com/success?user_id={user_id}',
            cancel_url='https://yourapp.com/cancel',
            metadata={'user_id': str(user_id)}
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'isBase64Encoded': False,
            'body': json.dumps({
                'payment_url': session.url,
                'session_id': session.id
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
