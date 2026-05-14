import base64
import json
import os
import requests
import pymysql
from datetime import datetime

# Cloud SQL configuration
db_user = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_HOST_NAME')
db_connection_name = os.getenv('INSTANCE_CONNECTION_NAME')

# Mailgun configuration
mailgun_domain = os.getenv('MAILGUN_DOMAIN')
mailgun_api_key = os.getenv('MAILGUN_API_KEY')
mailgun_sender_email = os.getenv('MAILGUN_SENDER_EMAIL')

def send_email(to_addr, subject, body):
    """Function to send an email using the Mailgun API."""
    response = requests.post(
        f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
        auth=("api", mailgun_api_key),
        data={"from": mailgun_sender_email,
              "to": to_addr,
              "subject": subject,
              "text": body}
    )
    return response

def generate_verification_link(user_uuid):
    """Function to generate a verification link."""
    return f"https://saivivekanand.me/v1/user/verify_email?token={user_uuid}"

def record_email_sent_time(user_uuid, email):
    """Function to record the email sent time into the Cloud SQL database."""
    # Connect to the database
    conn = pymysql.connect(user=db_user, password=db_password,
                           host=db_name,
                           db=db_user)
    with conn.cursor() as cursor:
        email_sent_time = datetime.utcnow()
        cursor.execute('''
            INSERT INTO verification_info (id, username, email_exp_time)
            VALUES (UNHEX(REPLACE(%s, '-', '')), %s, %s)
            ON DUPLICATE KEY UPDATE email_exp_time = VALUES(email_exp_time)
        ''', (user_uuid, email, email_sent_time))
        conn.commit()
    conn.close()

def hello_pubsub(event, context):
    """Cloud Function to be triggered by Pub/Sub that sends a verification email."""
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    user_info = json.loads(pubsub_message)

    # Generate a verification link using the UUID as the unique token
    verification_link = generate_verification_link(user_info['uuid'])

    # Construct the email body
    email_body = f"Hello {user_info.get('firstName', '')},\nPlease click on the link to verify your email: {verification_link}"

    # Send the verification email
    response = send_email(
        to_addr=user_info['username'],
        subject="Please verify your email",
        body=email_body
    )

    # Log the response and record the email sent time if successful
    if response.status_code == 200:
        print(f"Email sent to {user_info['username']}")
        record_email_sent_time(user_info['uuid'], user_info['username'])
    else:
        print(f"Failed to send email, status code: {response.status_code}, message: {response.text}")
