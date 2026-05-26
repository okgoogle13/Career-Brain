import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

creds = service_account.Credentials.from_service_account_file(
    "credentials.json", scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=creds)

about = drive_service.about().get(fields="storageQuota,user").execute()
print(f"User: {about['user']['emailAddress']}")
quota = about['storageQuota']
limit = int(quota.get('limit', 0))
usage = int(quota.get('usage', 0))
usage_in_drive = int(quota.get('usageInDrive', 0))
usage_in_drive_trash = int(quota.get('usageInDriveTrash', 0))

print(f"Limit: {limit / (1024**3):.2f} GB")
print(f"Usage: {usage / (1024**3):.2f} GB")
print(f"In Trash: {usage_in_drive_trash / (1024**3):.2f} GB")

if usage_in_drive_trash > 0:
    print("Emptying trash...")
    drive_service.files().emptyTrash().execute()
    print("Trash emptied!")
