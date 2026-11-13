"""Optional Drive upload; requires service account with write access to target folder."""
import json,os
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
info=json.loads(os.environ['GDRIVE_SA_JSON'])
folder=os.environ['GDRIVE_FOLDER_ID']
creds=service_account.Credentials.from_service_account_info(info,scopes=['https://www.googleapis.com/auth/drive.file'])
service=build('drive','v3',credentials=creds)
for name in ['pilot.mp4','qa.json']:
    path=Path('automation/pilot/output')/name
    mime='video/mp4' if name.endswith('.mp4') else 'application/json'
    created=service.files().create(body={'name':name,'parents':[folder]},media_body=MediaFileUpload(str(path),mimetype=mime,resumable=True),fields='id,name,parents,size,webViewLink',supportsAllDrives=True).execute()
    verified=service.files().get(fileId=created['id'],fields='id,name,parents,size,webViewLink',supportsAllDrives=True).execute()
    assert folder in verified['parents'] and verified['name']==name and int(verified['size'])==path.stat().st_size
    print(json.dumps(verified))
