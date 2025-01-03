import os.path
import pandas as pd
import base64
from bs4 import BeautifulSoup

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#from https://developers.google.com/gmail/api/quickstart/python
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
def authenticate():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

#modified version of https://medium.com/@preetipriyanka24/how-to-read-emails-from-gmail-using-gmail-api-in-python-20f7d9d09ae9
def fetch_and_create(service, max_results=250):
    # List of messages
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages')
    email_data = []
    
    for message in messages:
        # Get a message from its ID in the dictionary
        msg = service.users().messages().get(userId='me', id=message['id']).execute()

        # Avoid errors
        try:
            # Main content of email
            payload = msg['payload']
            headers = payload['headers']
            
            # Extract the Subject and Sender of the email
            email_info = {'id': message['id']}
            for header in headers:
                if header['name'] == 'Subject':
                    email_info['Subject'] = header['value']
                elif header['name'] == 'From':
                    email_info['From'] = header['value']
            
            # Decode the message body
            parts = payload.get('parts', [])[0]
            data = parts['body']['data']
            data = data.replace("-", "+").replace("_", "/")
            decoded_data = base64.b64decode(data).decode('utf-8')

            # Parse with BeautifulSoup and remove html code
            soup = BeautifulSoup(decoded_data, "lxml")
            body_text = soup.get_text()

            # Clean the text
            body_text = body_text.strip()
            body_text = body_text.replace('\n', ' ').replace('\r', ' ')
            body_text = ' '.join(body_text.split())

            email_info['Body'] = body_text

            email_data.append(email_info)
        except:
            pass

    return pd.DataFrame(email_data)

def main():
    service = authenticate()
    df = fetch_and_create(service, 250)
    df.to_csv('my_emails.csv', index = False)
    print("Success!")

if __name__ == "__main__":
    main()