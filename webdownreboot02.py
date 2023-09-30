# Sources Used:
# 1. https://developers.google.com/gmail/api/reference/rest/v1/users.messages/list
# 2. https://learndataanalysis.org/google-py-file-source-code/
# 3. https://thepythoncode.com/article/use-gmail-api-in-python
# 4. https://stackoverflow.com/questions/74487595/read-full-message-in-email-with-gmail-api
# 5. https://stackoverflow.com/questions/65304053/marking-emails-as-read-using-python-and-gmail-api


import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


def create_service(client_secret_file, api_name, api_version, *scopes, prefix=''):
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    
    creds = None
    working_dir = os.getcwd()
    token_dir = 'token files'
    token_file = f'token_{API_SERVICE_NAME}_{API_VERSION}{prefix}.json'

    ### Check if token dir exists first, if not, create the folder
    if not os.path.exists(os.path.join(working_dir, token_dir)):
        os.mkdir(os.path.join(working_dir, token_dir))

    if os.path.exists(os.path.join(working_dir, token_dir, token_file)):
        creds = Credentials.from_authorized_user_file(os.path.join(working_dir, token_dir, token_file), SCOPES)
        # with open(os.path.join(working_dir, token_dir, token_file), 'rb') as token:
        #   cred = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(os.path.join(working_dir, token_dir, token_file), 'w') as token:
            token.write(creds.to_json())

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=creds, static_discovery=False)
        print(API_SERVICE_NAME, API_VERSION, 'service created successfully')
        return service
    except Exception as e:
        print(e)
        print(f'Failed to create service instance for {API_SERVICE_NAME}')
        os.remove(os.path.join(working_dir, token_dir, token_file))
        return None

def main():
    CLIENT_FILE = 'credentials.json'
    API_NAME = 'gmail'
    API_VERSION = 'v1'
    SCOPES = ['https://mail.google.com/']
    EMAIL_FILTER = '<alerts@uptrends.com> is:unread'

    service = create_service(CLIENT_FILE, API_NAME, API_VERSION, SCOPES)
    if not service:  # Skipping any errors that would come up when no service is returned
        return 
    
    list_of_emails_found = service.users().messages().list(userId='me', q=EMAIL_FILTER).execute()  # returns a dict
    messages_data = list_of_emails_found.get('messages')  # returns a list
    
    if not messages_data:  # No specific emails was found in the inbox 
        return
    
    top_email_data = messages_data[0]
    email_id = top_email_data.get('id')
    raw_message = service.users().messages().get(userId='me', id=email_id, format='raw').execute()
    part_of_email_body = raw_message.get("snippet")
    
    # Marking Email as Read
    service.users().messages().modify(userId='me', id=email_id, body={'removeLabelIds': ['UNREAD']}).execute()
    
    if 'Error: 2000 - TCP connection timed out Monitor' in part_of_email_body:
        os.system("shutdown /r /t 1") # Restart Server in one second
    
        
if __name__ == "__main__":
    main()
    


# 