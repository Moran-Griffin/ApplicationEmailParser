import pandas as pd
import re
import base64
from bs4 import BeautifulSoup
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from quickstart import main as authenticate

'''
Pull max_results most recent emails from the associated gmail account
extract the ID, Sender, Body, and Subject, and clean the body text for use in the NLP model
The result is then stored in a pandas dataframe

This method will access emails over the span of multiple pages as needed and only accesses mail
in the primary category, last checked can be used to specify the date of the least recently received email
it is a modified version of https://medium.com/@preetipriyanka24/how-to-read-emails-from-gmail-using-gmail-api-in-python-20f7d9d09ae9
'''
def fetch_and_create(service, last_checked, max_results=250):
    last_checked = int(last_checked)
    query = f"after:{last_checked}"
     
    if last_checked != 0:
        results = service.users().messages().list(
            userId='me',
            q=f"{query} category:primary",
            maxResults=max_results,
            labelIds=['INBOX']).execute()
    else:
        results = service.users().messages().list(
            userId='me',
            q='category:primary',
            maxResults=max_results,
            labelIds=['INBOX']).execute()
    messages = results.get('messages', [])
    email_data = []
    
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        try:
            payload = msg['payload']
            headers = payload['headers']
                
            email_info = {'id': message['id']}
            for header in headers:
                if header['name'] == 'Subject':
                    email_info['Subject'] = header['value']
                elif header['name'] == 'From':
                    email_info['From'] = header['value']
                
            parts = payload.get('parts', [])[0]
            data = parts['body']['data']
            data = data.replace("-", "+").replace("_", "/")
            decoded_data = base64.b64decode(data).decode('utf-8')

            soup = BeautifulSoup(decoded_data, "lxml")
            body_text = soup.get_text()
            body_text = body_text.strip()
            body_text = body_text.replace('\n', ' ').replace('\r', ' ')
            body_text = ' '.join(body_text.split())
            body_text = re.sub(r'[^\x20-\x7E]', '', body_text)

            email_info['Body'] = body_text
            email_data.append(email_info)
        except:
            pass
    return pd.DataFrame(email_data)

'''
Main method used to create csv files to be used in excel to finalize the dataset
that would be used in my NLP model
'''
def main():
    service = authenticate()
    df = fetch_and_create(service, 0, 550)
    df.to_csv('my_emails_big.csv', index = False)
    print("Success!")

if __name__ == "__main__":
    main()