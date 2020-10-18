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
import textwrap
import sys

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

if len(sys.argv) < 2:
    print("Usage: python download-doc.py [doc ID]")
    sys.exit(1)

DOCUMENT_ID = sys.argv[1]

DOCUMENT_PICKLE_FILE = 'document-body-' + DOCUMENT_ID + '.pickle'
DOCUMENT_TEX_FILE = 'document-body-' + DOCUMENT_ID + '.tex'

def auth_and_download_body():
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
    document = service.documents().get(documentId=DOCUMENT_ID).execute()

    print('The title of the document is: {}'.format(document.get('title')))

    with open(DOCUMENT_PICKLE_FILE, 'wb') as body_pickle:
        pickle.dump(document.get('body'), body_pickle)

def process_body():
    document_body = None

    with open(DOCUMENT_PICKLE_FILE, 'rb') as body_pickle:
        document_body = pickle.load(body_pickle)

    with open(DOCUMENT_TEX_FILE, 'w') as body_tex:
        for k in document_body['content']:
            if 'paragraph' in k:
                process_paragraph(k['paragraph'], body_tex)
            elif 'sectionBreak' in k:
                # ignore
                pass
            else:
                print(k)

p_wrap = textwrap.TextWrapper(width = 70, break_long_words = False, break_on_hyphens = False)

def process_paragraph(para, body_tex):
    if para['paragraphStyle']['namedStyleType'].startswith("HEADING_"):
        headingTags = {
            'HEADING_2': 'section',
            'HEADING_3': 'subsection',
            'HEADING_4': 'subsubsection'
        }

        tag = headingTags[para['paragraphStyle']['namedStyleType']]

        content = process_elements(para['elements'])

        latex_out = "\\%s*{%s}\n" % (tag, content)
        body_tex.write(latex_out)

    elif 'indentStart' in para['paragraphStyle']:
        # ignore
        pass
    elif para['paragraphStyle']['namedStyleType'] == "NORMAL_TEXT":
        content = process_elements(para['elements'])
        if content != "":
            for l in p_wrap.wrap(content):
                body_tex.write(l + "\n")
            body_tex.write("\n")

    elif para['paragraphStyle']['namedStyleType'] == "TITLE":
        # ignore
        pass
    else:
        print(para['paragraphStyle'])
    #print(para)

def process_elements(elements):

    char_replace = {
        u'\u2019': '\'',
        u'\u201c': '``',
        u'\u201d': '\'\'',
        u'\u2014': '---',
        u'$': '\\$',
    }

    content = ""

    for e in elements:
        el_content = e['textRun']['content']

        for (f, t) in char_replace.items():
            el_content = el_content.replace(f, t)

        if e['textRun']['textStyle'] != {}:
            if e['textRun']['textStyle'].get('baselineOffset') == 'SUBSCRIPT':
                el_content = "\\textsubscript{%s}" % (el_content)
            elif 'backgroundColor' in e['textRun']['textStyle']:
                # ignore test highlight
                pass
            else:
                print("TEXT STYLE:", e['textRun']['textStyle'])


        content += el_content

    return content.strip()

if __name__ == '__main__':
    #if not os.path.exists(DOCUMENT_PICKLE_FILE):
    print("Downloading document ... ")
    auth_and_download_body()

    process_body()

# [END docs_quickstart]
