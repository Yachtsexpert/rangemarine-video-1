"""Upload pilot outputs to Drive using a short-lived GitHub OIDC access token."""
import json
import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

token = os.environ['GDRIVE_ACCESS_TOKEN']
folder = os.environ['GDRIVE_FOLDER_ID']
run_id = os.environ['GITHUB_RUN_ID']
run_attempt = os.environ.get('GITHUB_RUN_ATTEMPT', '1')
creds = Credentials(token=token)
service = build('drive', 'v3', credentials=creds, cache_discovery=False)
outputs = Path('automation/pilot/output')

for local_name, suffix, mime in [
    ('pilot.mp4', 'mp4', 'video/mp4'),
    ('qa.json', 'qa.json', 'application/json'),
]:
    path = outputs / local_name
    drive_name = f'technical-pilot-{run_id}-{run_attempt}.{suffix}'
    created = service.files().create(
        body={'name': drive_name, 'parents': [folder]},
        media_body=MediaFileUpload(str(path), mimetype=mime, resumable=True),
        fields='id,name,parents,size,webViewLink',
        supportsAllDrives=True,
    ).execute()
    verified = service.files().get(
        fileId=created['id'],
        fields='id,name,parents,size,webViewLink',
        supportsAllDrives=True,
    ).execute()
    assert folder in verified['parents']
    assert verified['name'] == drive_name
    assert int(verified['size']) == path.stat().st_size
    print(json.dumps(verified, sort_keys=True))
