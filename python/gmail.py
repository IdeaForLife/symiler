from __future__ import print_function
import base64
import pickle
import os.path
from bs4 import BeautifulSoup
from bs4.element import Comment
import html2text
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    results = service.users().messages().list(userId='me',maxResults='5',q='category:promotions').execute()
    #print(results)
    messages = results.get('messages', [])

    if not messages:
        print('No promotions found.')
    else:
        print('messages:')
        for id in messages:
            # Get message content
            message = service.users().messages().get(userId='me',id=id['id'], format="raw").execute()
            #print(message)
            #mssg_parts = message['payload']['parts'] # fetching the message parts
           # part_one  = mssg_parts[0] # fetching first element of the part 
            #part_body = part_one['body'] # fetching body of the message
            part_data = message['raw'] # fetching data from the body
            clean_one = part_data.replace("-","+") # decoding from Base64 to UTF-8
            clean_one = clean_one.replace("_","/") # decoding from Base64 to UTF-8
            clean_two = base64.b64decode (bytes(clean_one, 'UTF-8')) # decoding from Base64 to UTF-8
            #print(clean_two)
            soup = BeautifulSoup(clean_two , 'html.parser' )
            #mssg_body = soup.body()
            # mssg_body is a readible form of message body
            # depending on the end user's requirements, it can be further cleaned 
            # using regex, beautiful soup, or any other method
            visible_texts = filter(tag_visible, soup.findAll(text=True))
            print(u" ".join(t.strip() for t in visible_texts))

if __name__ == '__main__':
    main()