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
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sys

import converters.latex

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

def auth_and_download_body(doc_id, doc_pickle_file):
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
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
            creds = flow.run_console()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('docs', 'v1', credentials=creds)

    # Retrieve the documents contents from the Docs service.
    document = service.documents().get(documentId=doc_id).execute()

    print('The title of the document is: {}'.format(document.get('title')))

    with open(doc_pickle_file, 'wb') as body_pickle:
        pickle.dump(document.get('body'), body_pickle)


if __name__ == '__main__':

    if len(sys.argv) != 4:
        print("Usage: docker run [...] download-doc.py [doc-id] [latex,markdown] [out-file]")
        sys.exit(1)

    doc_id = sys.argv[1]
    format = sys.argv[2]
    out_file = sys.argv[3]

    doc_pickle_file = 'document-body-' + doc_id + '.pickle'

    if not os.path.exists(doc_pickle_file):
        print("Downloading document ... ")
        auth_and_download_body(doc_id, doc_pickle_file)

    if format == "latex":
        converters.latex.process_body(doc_pickle_file, out_file)

# [END docs_quickstart]
