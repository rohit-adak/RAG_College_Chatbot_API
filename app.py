import os
import time
from datetime import datetime
import pandas as pd
import psycopg2
import requests
from dotenv import load_dotenv
from flask import Flask, request

from database import connect_db, login_temp_query
from gen_ai_model import ask_ai

load_dotenv()
app = Flask(__name__)
whatsapp_token = os.environ.get('META_API_KEY')
api_access_token = os.environ.get('API_ACCESS_TOKEN')
api_secret_key = os.environ.get('API_SECRET_KEY')

whatsapp_url = "https://graph.facebook.com/v15.0/118747294485912/messages"


def send_whatsapp_message(message=False, temp_msg=False):
    """
    Sends a WhatsApp message using the Facebook Graph API.

    Args:
        message (str, optional): The message content to be sent.
        temp_msg (bool, optional): Flag indicating whether to send a template message.

    Returns:
        str: Response text from the API call.
    """

    # Set headers for the request including authorization with the WhatsApp token
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {whatsapp_token}'
    }

    # Construct payload based on whether it's a template message or not
    if (not temp_msg) and message:
        payload = {
            "messaging_product": "whatsapp",
            "to": "919819342606",
            "type": "text",
            "text": {
                "preview_url": "true",
                "body": message
            },
        }
    else:
        payload = {
            "messaging_product": "whatsapp",
            "to": "919819342606",
            "type": "template",
            "template": {
                "name": "hello_world",
                "language": {
                    "code": "en_US"
                }
            }
        }
            # Send the POST request to the WhatsApp API
    response = requests.post(whatsapp_url, headers=headers, json=payload)
    
    # Return the response text
    return response.text



@app.route('/hc')
def health_check():
    """
    Endpoint for performing a health check.

    Returns:
        str: 'UP' indicating the service is up and running.
    """
    return 'UP'

@app.route('/webhook', methods=['GET', 'POST'])
def webhook_manager():
    """
    Endpoint for managing webhooks from WhatsApp.

    Returns:
        str or dict: Response based on the request method.
    """
    if request.method == 'GET':
        hub_challenge = request.args.get('hub.challenge')
        hub_verification = request.args.get('hub.verify_token')
        if hub_challenge and hub_verification == 'python is best':
            return hub_challenge
        else:
            return {"message": "Webhook Manager"}
    elif request.method == 'POST':
        data = request.json
        try: 
            user_query = data['entry'][0]['changes'][0]['value']['messages'][0]
            conversationId = data['entry'][0]['id']
            msg_from = user_query['from']
            msg_time = user_query['timestamp']
            msg = user_query['text']['body']
            msg_type = user_query['type']

            response = ask_ai(msg,
                            id=conversationId,
                            source='Whatsapp',
                            time_stamp=datetime.fromtimestamp(int(msg_time)),
                            user=msg_from)
            send_whatsapp_message(message=response, temp_msg=False)
        except:
            pass
        return {'status': 'success'}


@app.route('/get_logs', methods=['POST'])
def get_logs():
    """
    Endpoint for retrieving chatbot logs.

    Returns:
        dict: JSON logs or error message.
    """
    try:
        request_data = request.json

        if (request_data["access_token"] == api_access_token and \
                request_data["secret_key"] == api_secret_key):
            
            query = "SELECT * FROM chatbot_logs"
            
            try:
                connection = connect_db()
                df = pd.read_sql(query, connection)
                json_logs = df.to_json()

                connection.close()

                return json_logs
            except psycopg2.Error:
                return {'error': 'database error'}

        else:
            return {'error': 'Invalid Authentication'}
    except:
        return {'error': 'Invalid JSON Query'}
    
        

@app.route("/user_auth", methods=['POST'])
def user_login():
    """
    Endpoint for user authentication.

    Returns:
        dict: JSON response indicating if the user is valid or not.
    """
    try:
        request_data = request.json
        if (request_data.get("access_token") == api_access_token and \
                    request_data.get("secret_key") == api_secret_key):
           
            current_time = time.strftime("%I:%M %p", time.localtime())
            login_credentials = request_data.get('login_creds', {})
            email = login_credentials.get('email', '')
            password = login_credentials.get('password', '')

            login_query = login_temp_query.format(
                first_login=current_time,
                last_login=current_time,
                email=email,
                password=password
            )

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute(login_query)
            conn.commit()

            is_valid_user = cursor.rowcount == 1
            return {"is_valid_user": is_valid_user}

    except BaseException as e:
        return {"error": "Invalid JSON query", "desc": str(e)}



@app.route("/chat_ai", methods=['POST'])
def ai_chat():
    """
    Endpoint for AI chat.

    Returns:
        dict: JSON response containing AI chat responses or error message.
    """
    try:
        request_data = request.json

        if (request_data["access_token"] == api_access_token and \
                request_data["secret_key"] == api_secret_key):

            if request_data['model'] == 'bscit_g_query':
                queries = request_data['queries']
                print(request_data)
                response = {"response data":
                            [{'id': r['id'], 'response': ask_ai(
                                user_question=r['prompt'], id=r['id'], 
                                source='Web Portal', 
                                user=r['user'],
                                load_class= False
                                )} for r in queries]
                            }
            elif request_data['model'] == 'bscit_c_query':
                queries = request_data['queries']
                response = {"response data":
                            [{'id': r['id'], 'response': ask_ai(
                                user_question=r['prompt'], id=r['id'], 
                                source='Web Portal', 
                                user=r['user'],
                                load_class= True
                                )} for r in queries]
                            }

                return response
            else:
                return {"error": "invalid model name"}


        else:
            return {"error": "Invalid Authentication"}
    except:
        return {"error": "Invalid JSON Query"}

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=10000)
