import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config import Settings


class StorageService:
    ALLOWED_CONTENT_TYPES = {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    def __init__(self, settings: Settings) -> None:
        self._base_path = Path(settings.storage_path)
        self._max_size = settings.max_upload_size

    def ensure_base_dir(self) -> None:
        self._base_path.mkdir(parents=True, exist_ok=True)

    def validate_upload(self, file: UploadFile, content: bytes) -> None:
        if len(content) > self._max_size:
            from app.exceptions import AppError

            raise AppError(413, "ファイルサイズが上限を超えています", "FILE_TOO_LARGE")
        content_type = file.content_type or ""
        if content_type not in self.ALLOWED_CONTENT_TYPES:
            from app.exceptions import AppError

            raise AppError(400, "許可されていないファイル形式です", "FILE_TYPE_NOT_ALLOWED")

    def save_file(self, aid: int, contract_id: int, file_name: str, content: bytes) -> str:
        self.ensure_base_dir()
        relative_dir = Path(str(aid)) / str(contract_id)
        absolute_dir = self._base_path / relative_dir
        absolute_dir.mkdir(parents=True, exist_ok=True)
        stored_name = f"{uuid.uuid4().hex}_{file_name}"
        relative_path = relative_dir / stored_name
        absolute_path = self._base_path / relative_path
        absolute_path.write_bytes(content)
        return relative_path.as_posix()

    def resolve_path(self, storage_path: str) -> Path:
        return self._base_path / storage_path

    def delete_file(self, storage_path: str) -> None:
        path = self.resolve_path(storage_path)
        if path.exists():
            path.unlink()
