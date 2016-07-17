from __future__ import print_function
import httplib2
import os

import requests


from apiclient import discovery
from apiclient.http import MediaFileUpload
from apiclient.errors import ResumableUploadError
import oauth2client
from oauth2client import client
from oauth2client import tools

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive.file'
CLIENT_SECRET_FILE = 'credentials.json'
APPLICATION_NAME = 'Drive API Python Quickstart'
flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=SCOPES, redirect_uri='http://localhost:3000/callback')

def get_authorize_url():
    auth_uri = flow.step1_get_authorize_url()
    return auth_uri

def authorize_code(code):
    credentials = flow.step2_exchange(code)
    http = httplib2.Http()
    http = credentials.authorize(http)
    return http

def create_folder(http, folder_name):
    drive_service = discovery.build('drive', 'v3', http=http)
    file_metadata = {
      'name' : folder_name,
      'mimeType' : 'application/vnd.google-apps.folder'
    }
    file = drive_service.files().create(body=file_metadata, fields='id').execute()
    return file.get('id')

def upload_file(file_path, file_name, folder_id, http):
    # Create Google Drive service instance
    drive_service = discovery.build('drive', 'v3', http=http)
    # File body description
    media_body = MediaFileUpload(file_path,
                                 mimetype='application/zip',
                                 resumable=True)
    body = {
        'name': file_name,
        'description': 'backup',
        'mimeType': 'application/zip',
        'parents': [ folder_id ]
    }
    # Permissions body description: anyone who has link can upload
    # Other permissions can be found at https://developers.google.com/drive/v2/reference/permissions
    permissions = {
        'role': 'reader',
        'type': 'anyone',
        'value': None,
        'withLink': True
    }
    # Insert a file
    file = drive_service.files().create(body=body, media_body=media_body).execute()
    # Insert new permissions
    # drive_service.permissions().create(fileId=file['id'], body=permissions).execute()
    # Define file instance and get url for download
    print(file.get('id'))
    return None

def get_url_list(filename):
    lines = open('stock_templates.txt').read().splitlines()
    return lines

def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return local_filename
def main():
    print("Go to url : " + get_authorize_url())
    code = input('Enter user code: ')
    http = authorize_code(code)
    folder_id = create_folder(http, 'Test Folder')
    urls = get_url_list('stock_templates.txt')
    for url in urls:
        file_name = download_file(url)
        upload_file(file_name, file_name, folder_id, http)
        os.remove(file_name)

if __name__ == '__main__':
    main()