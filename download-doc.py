# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START docs_quickstart]
from __future__ import print_function
import pickle
import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import sys

import converters.latex
import converters.markdown

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

def auth_and_download_body(doc_id):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('docs', 'v1', credentials=creds)

        # Retrieve the documents contents from the Docs service.
        document = service.documents().get(documentId=doc_id).execute()

        print('The title of the document is: {}'.format(document.get('title')))

        return document.get('body')

    except HttpError as err:
        print(err)

def crawl(path):
    pass

def download(doc_id, out_file):
    print("Downloading document ... ")
    doc_body = auth_and_download_body(doc_id)

    converters.markdown.process_body_raw(doc_body, out_file)


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("Usage: docker run [...] download-doc.py [doc-id] [out-file]")
        print("Usage: docker run [...] download-doc.py crawl [path]")
        sys.exit(1)

    command = sys.argv[1] 

    if command == "crawl":
        path = sys.argv[2]
        crawl(path)
    else:
        doc_id = sys.argv[1]
        out_file = sys.argv[2]
        download(doc_id, out_file)

