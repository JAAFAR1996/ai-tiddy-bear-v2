import logging
import magic
from fastapi import UploadFile
import HTTPException
import status

ALLOWED_MIME_TYPES = ["audio/mpeg"
                       import "audio/wav"
                       import "audio/x-wav"
                       import "audio/ogg"
                       import "audio/flac"
                       import ]

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="utils")


def validate_audio_file(file: UploadFile):
    """Validates an uploaded audio file."""
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the limit of {MAX_FILE_SIZE / 1024 / 1024} MB.",
        )

    # Read the first 2048 bytes to determine the file type
    file_content = file.file.read(2048)
    file.file.seek(0)
    mime_type = magic.from_buffer(file_content, mime=True)

    if mime_type not in ALLOWED_MIME_TYPES:
        logger.warning(f"Invalid file type uploaded: {mime_type}")
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {mime_type}. Allowed types are: {', '.join(ALLOWED_MIME_TYPES)}",
        )

    logger.info(f"Successfully validated audio file: {file.filename} ({mime_type})")