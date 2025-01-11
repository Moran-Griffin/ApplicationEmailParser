import joblib
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from model import text_process
from quickstart import main as authenticate
from setup import fetch_and_create

'''
Create a Gmail label of a user-defined name
Returns the ID of the label for future access
'''
def create_label(service, name):
    label = {
        'name': name,
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show'
    }
    created = service.users().labels().create(userId='me', body=label).execute()
    return created['id']

#Use the NLP model to classify emails, if they are internship related, apply the desired label to them, else ignore them
def parser(service, emails, model, label_id):
    labeled = 0
    for index, row in emails.iterrows():
        category = model.predict([row['Body']])
        if category == 1:
            labeled += 1
            service.users().messages().modify(
                userId='me',
                id=row['id'],
                body={'addLabelIds': [label_id]}
            ).execute()
    return labeled

'''
Uses the imported NLP model after authentication to repeatedly classify emails since last use of the application (all emails if first use)
check for new emails every minute and classify them if applicable
'''
def main():
    model = joblib.load("mail_model.pkl")
    service = authenticate()
    last = joblib.load("last_checked.pkl")
    quit = False
    id = 'Label_8669670635772513532'

    #Uncomment if running for the first time
    #id = create_label(service, 'Internship Info')

    profile = service.users().getProfile(userId='me').execute()
    print("Connected Gmail Account: ", profile['emailAddress'])
    print('\nType "Quit" to end the program.')

    while not quit:
        emails = fetch_and_create(service = service, last_checked = last)
        if not emails.empty:
            labeled = parser(service, emails, model, id)
            print(f"Successfully labeled {labeled} email/s.")
        last = int(time.time())
        joblib.dump(value = last, filename = "last_checked.pkl")
        time.sleep(60)

if __name__ == "__main__":
    main()
