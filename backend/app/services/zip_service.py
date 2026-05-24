"""
ZipService — bundles all generated project files into a downloadable ZIP archive.
"""
import io
import os
import zipfile
from pathlib import Path
from loguru import logger
from app.core.config import settings


class ZipService:

    def create_zip_bytes(self, files: dict[str, str]) -> bytes:
        """
        Takes {filepath: content} dict and returns ZIP as raw bytes.
        Used for streaming download without writing to disk.
        """
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path, content in files.items():
                # Normalise path separators
                clean_path = file_path.replace("\\", "/").lstrip("/")
                if content is None:
                    content = ""
                zf.writestr(clean_path, content)
                logger.debug(f"  ZIP: added {clean_path} ({len(content)} bytes)")
        buffer.seek(0)
        logger.info(f"ZIP created: {len(files)} files, {buffer.getbuffer().nbytes} bytes")
        return buffer.getvalue()

    def save_zip_to_disk(
        self, project_id: str, files: dict[str, str]
    ) -> str:
        """
        Writes ZIP to GENERATED_FILES_DIR and returns the path.
        Used for persistent storage after generation.
        """
        output_dir = Path(settings.GENERATED_FILES_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)

        zip_path = output_dir / f"{project_id}.zip"
        with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path, content in files.items():
                clean_path = file_path.replace("\\", "/").lstrip("/")
                zf.writestr(clean_path, content or "")

        logger.info(f"ZIP saved: {zip_path}")
        return str(zip_path)


zip_service = ZipService()
