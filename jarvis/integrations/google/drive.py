import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from loguru import logger


class GoogleDrive:
    def __init__(self, creds):
        self.service = build("drive", "v3", credentials=creds)

    def search_files(self, query: str = "", max_results: int = 10) -> list[dict]:
        results = self.service.files().list(
            q=query,
            pageSize=max_results,
            fields="files(id, name, mimeType, modifiedTime, size)",
        ).execute()
        return results.get("files", [])

    def upload_file(self, file_path: str, folder_id: str = None) -> str:
        file_name = os.path.basename(file_path)
        media = MediaFileUpload(file_path, resumable=True)
        file_metadata = {"name": file_name}
        if folder_id:
            file_metadata["parents"] = [folder_id]
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id",
        ).execute()
        logger.info(f"Uploaded {file_name} to Drive (ID: {file['id']})")
        return f"Uploaded {file_name} to Google Drive"

    def download_file(self, file_id: str, destination: str) -> str:
        request = self.service.files().get_media(fileId=file_id)
        with open(destination, "wb") as f:
            f.write(request.execute())
        logger.info(f"Downloaded file {file_id} to {destination}")
        return f"Downloaded file to {destination}"

    def list_recent(self, max_results: int = 10) -> list[dict]:
        return self.search_files(
            query="trashed=false",
            max_results=max_results,
        )

    def get_recent_summary(self) -> str:
        files = self.list_recent(max_results=5)
        if not files:
            return "No files found in Google Drive"
        parts = []
        for f in files:
            parts.append(f"{f['name']} ({f.get('mimeType', 'unknown')})")
        return f"Recent Drive files: {'; '.join(parts)}"

    def create_folder(self, folder_name: str, parent_id: str = None) -> str:
        file_metadata = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder"}
        if parent_id:
            file_metadata["parents"] = [parent_id]
        folder = self.service.files().create(body=file_metadata, fields="id").execute()
        logger.info(f"Drive folder created: {folder_name}")
        return f"Created folder '{folder_name}' in Google Drive"

    def move_file(self, file_id: str, new_folder_id: str) -> str:
        file = self.service.files().get(fileId=file_id, fields="parents").execute()
        previous_parents = ",".join(file.get("parents", []))
        self.service.files().update(fileId=file_id, addParents=new_folder_id, removeParents=previous_parents, fields="id, parents").execute()
        logger.info(f"File {file_id} moved to folder {new_folder_id}")
        return f"Moved file to new folder"

    def share_file(self, file_id: str, email: str, role: str = "writer") -> str:
        permission = {"type": "user", "role": role, "emailAddress": email}
        self.service.permissions().create(fileId=file_id, body=permission).execute()
        logger.info(f"File {file_id} shared with {email}")
        return f"Shared file with {email} as {role}"
