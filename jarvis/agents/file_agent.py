import os
import shutil
import glob
from datetime import datetime
from loguru import logger


class FileAgent:
    name = "file_agent"
    description = "Manages files and folders: create, delete, move, rename, search, list contents"

    def list_directory(self, path: str = ".") -> str:
        try:
            entries = os.listdir(path)
            dirs = [e for e in entries if os.path.isdir(os.path.join(path, e))]
            files = [e for e in entries if os.path.isfile(os.path.join(path, e))]
            result = f"Directory: {path}\n"
            if dirs:
                result += f"Folders ({len(dirs)}): {', '.join(dirs[:20])}\n"
            if files:
                result += f"Files ({len(files)}): {', '.join(files[:20])}"
            return result.strip()
        except Exception as e:
            return f"Failed to list directory: {e}"

    def create_directory(self, path: str) -> str:
        try:
            os.makedirs(path, exist_ok=True)
            logger.info(f"Created directory: {path}")
            return f"Created directory {path}"
        except Exception as e:
            return f"Failed to create directory: {e}"

    def create_file(self, path: str, content: str = "") -> str:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Created file: {path}")
            return f"Created file {path}"
        except Exception as e:
            return f"Failed to create file: {e}"

    def read_file(self, path: str, max_lines: int = 100) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            content = "".join(lines[:max_lines])
            if len(lines) > max_lines:
                content += f"\n... ({len(lines) - max_lines} more lines)"
            return content
        except Exception as e:
            return f"Failed to read file: {e}"

    def delete_file(self, path: str) -> str:
        try:
            if os.path.isfile(path):
                os.remove(path)
                logger.info(f"Deleted file: {path}")
                return f"Deleted {path}"
            elif os.path.isdir(path):
                shutil.rmtree(path)
                logger.info(f"Deleted directory: {path}")
                return f"Deleted directory {path}"
            return f"Path not found: {path}"
        except Exception as e:
            return f"Failed to delete: {e}"

    def move_file(self, source: str, destination: str) -> str:
        try:
            shutil.move(source, destination)
            logger.info(f"Moved {source} to {destination}")
            return f"Moved {source} to {destination}"
        except Exception as e:
            return f"Failed to move: {e}"

    def rename_file(self, old_path: str, new_name: str) -> str:
        try:
            dir_name = os.path.dirname(old_path)
            new_path = os.path.join(dir_name, new_name)
            os.rename(old_path, new_path)
            logger.info(f"Renamed {old_path} to {new_path}")
            return f"Renamed to {new_name}"
        except Exception as e:
            return f"Failed to rename: {e}"

    def search_files(self, pattern: str, path: str = ".") -> str:
        try:
            search_path = os.path.join(path, pattern)
            matches = glob.glob(search_path, recursive=True)
            if not matches:
                return f"No files matching '{pattern}' in {path}"
            files = [m for m in matches if os.path.isfile(m)]
            dirs = [m for m in matches if os.path.isdir(m)]
            result = f"Found {len(matches)} matches for '{pattern}':\n"
            if dirs:
                result += f"Directories: {', '.join(dirs[:10])}\n"
            if files:
                result += f"Files: {', '.join(files[:20])}"
            return result.strip()
        except Exception as e:
            return f"Search failed: {e}"

    def get_file_info(self, path: str) -> str:
        try:
            stat = os.stat(path)
            size = stat.st_size
            if size > 1024 * 1024:
                size_str = f"{size / 1024 / 1024:.1f} MB"
            elif size > 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size} bytes"
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            return f"File: {path}\nSize: {size_str}\nModified: {modified}\nType: {'Directory' if os.path.isdir(path) else 'File'}"
        except Exception as e:
            return f"Failed to get file info: {e}"

    def bulk_rename(self, path: str, pattern: str, replacement: str) -> str:
        try:
            count = 0
            for filename in os.listdir(path):
                if pattern in filename:
                    new_name = filename.replace(pattern, replacement)
                    old_path = os.path.join(path, filename)
                    new_path = os.path.join(path, new_name)
                    os.rename(old_path, new_path)
                    count += 1
            logger.info(f"Bulk renamed {count} files in {path}: {pattern} -> {replacement}")
            return f"Renamed {count} files in {path}: '{pattern}' -> '{replacement}'"
        except Exception as e:
            return f"Bulk rename failed: {e}"

    def organize_by_extension(self, path: str) -> str:
        try:
            count = 0
            for filename in os.listdir(path):
                filepath = os.path.join(path, filename)
                if os.path.isfile(filepath):
                    ext = filename.split(".")[-1] if "." in filename else "other"
                    ext_dir = os.path.join(path, ext.upper() + "_files")
                    os.makedirs(ext_dir, exist_ok=True)
                    os.rename(filepath, os.path.join(ext_dir, filename))
                    count += 1
            logger.info(f"Organized {count} files by extension in {path}")
            return f"Organized {count} files into extension-based folders in {path}"
        except Exception as e:
            return f"Organize failed: {e}"

    def sort_downloads(self, downloads_path: str) -> str:
        try:
            categories = {
                "Images": [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".bmp"],
                "Documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx"],
                "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
                "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"],
                "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
                "Installers": [".exe", ".msi", ".dmg", ".deb", ".rpm"],
                "Code": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".html", ".css"],
            }
            count = 0
            for filename in os.listdir(downloads_path):
                filepath = os.path.join(downloads_path, filename)
                if os.path.isfile(filepath):
                    ext = os.path.splitext(filename)[1].lower()
                    for category, extensions in categories.items():
                        if ext in extensions:
                            cat_dir = os.path.join(downloads_path, category)
                            os.makedirs(cat_dir, exist_ok=True)
                            os.rename(filepath, os.path.join(cat_dir, filename))
                            count += 1
                            break
            logger.info(f"Sorted {count} downloads in {downloads_path}")
            return f"Sorted {count} files into categorized folders in {downloads_path}"
        except Exception as e:
            return f"Sort downloads failed: {e}"
