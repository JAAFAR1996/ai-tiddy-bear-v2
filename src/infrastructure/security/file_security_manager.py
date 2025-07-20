import hashlib
import mimetypes
import re
from pathlib import Path
from typing import Any

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class AudioFileSecurityManager:
    """Handles audio file validation and security checks."""

    def __init__(self) -> None:
        self.allowed_audio_types = ["wav", "mp3", "m4a", "ogg", "flac"]
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.blocked_extensions = [
            ".exe",
            ".bat",
            ".cmd",
            ".scr",
            ".jar",
            ".js",
            ".vbs",
            ".ps1",
        ]

    def validate_audio_file(self, filename: str, file_content: bytes) -> dict[str, Any]:
        """Validate audio file for security and format compliance.

        Args:
            filename: Name of the file
            file_content: File content as bytes
        Returns:
            Dict containing validation results

        """
        result = {
            "is_valid": False,
            "errors": [],
            "warnings": [],
            "file_info": {},
        }

        try:
            # Check file size
            if len(file_content) > self.max_file_size:
                result["errors"].append(
                    f"File size exceeds maximum allowed size of "
                    f"{self.max_file_size} bytes",
                )
                return result

            if len(file_content) == 0:
                result["errors"].append("File is empty")
                return result

            # Sanitize filename
            sanitized_filename = self.sanitize_filename(filename)
            if sanitized_filename != filename:
                result["warnings"].append(
                    f"Filename was sanitized from '{filename}' to '{sanitized_filename}'",
                )

            # Check file extension
            file_extension = Path(sanitized_filename).suffix.lower().lstrip(".")
            if file_extension not in self.allowed_audio_types:
                result["errors"].append(
                    f"File extension '{file_extension}' is not allowed. "
                    f"Allowed types: {', '.join(self.allowed_audio_types)}",
                )
                return result

            # Check for blocked extensions
            if any(
                sanitized_filename.lower().endswith(ext)
                for ext in self.blocked_extensions
            ):
                result["errors"].append(
                    "File extension is blocked for security reasons",
                )
                return result

            # Basic audio file validation using magic numbers
            validation_result = self._validate_audio_magic_numbers(
                file_content,
                file_extension,
            )
            if not validation_result["is_valid"]:
                result["errors"].extend(validation_result["errors"])
                return result

            # File passed all checks
            result["is_valid"] = True
            result["file_info"] = {
                "original_filename": filename,
                "sanitized_filename": sanitized_filename,
                "file_size": len(file_content),
                "file_type": file_extension,
                "mime_type": mimetypes.guess_type(sanitized_filename)[0]
                or "application/octet-stream",
                "file_hash": hashlib.sha256(file_content).hexdigest(),
            }

            logger.info(f"Audio file validation successful for {sanitized_filename}")
            return result
        except (ValueError, OSError, RuntimeError) as e:
            logger.error(f"Error validating audio file {filename}: {e}")
            result["errors"].append(f"Validation error: {e!s}")
            return result

    def _validate_audio_magic_numbers(
        self,
        file_content: bytes,
        expected_type: str,
    ) -> dict[str, Any]:
        """Validate audio file using magic numbers/headers."""
        result = {"is_valid": False, "errors": []}

        if len(file_content) < 12:
            result["errors"].append("File too small to contain valid audio header")
            return result

        # Check magic numbers for different audio formats
        header = file_content[:12]
        try:
            if expected_type == "wav":
                # WAV files start with "RIFF" and contain "WAVE"
                if header[:4] == b"RIFF" and header[8:12] == b"WAVE":
                    result["is_valid"] = True
                else:
                    result["errors"].append("Invalid WAV file header")
            elif expected_type == "mp3":
                # MP3 files can start with ID3v2 tag or audio frame
                if (
                    header[:3] == b"ID3"
                    or header[:2] == b"\xff\xfb"
                    or header[:2] == b"\xff\xf3"
                ):
                    result["is_valid"] = True
                else:
                    result["errors"].append("Invalid MP3 file header")
            elif expected_type == "m4a":
                # M4A files are MP4 containers
                if b"ftyp" in header[:12]:
                    result["is_valid"] = True
                else:
                    result["errors"].append("Invalid M4A file header")
            elif expected_type == "ogg":
                # OGG files start with "OggS"
                if header[:4] == b"OggS":
                    result["is_valid"] = True
                else:
                    result["errors"].append("Invalid OGG file header")
            elif expected_type == "flac":
                # FLAC files start with "fLaC"
                if header[:4] == b"fLaC":
                    result["is_valid"] = True
                else:
                    result["errors"].append("Invalid FLAC file header")
            # For other formats, just check that it's not executable
            elif not self._is_executable_file(header):
                result["is_valid"] = True
            else:
                result["errors"].append("File appears to be executable")
        except (ValueError, IndexError, TypeError) as e:
            result["errors"].append(f"Magic number validation error: {e!s}")

        return result

    def _is_executable_file(self, header: bytes) -> bool:
        """Check if file header indicates executable file."""
        # Common executable file headers
        executable_headers = [
            b"MZ",  # Windows PE
            b"\x7fELF",  # Linux ELF
            b"\xca\xfe\xba\xbe",  # Java class
            b"\xfe\xed\xfa\xce",  # Mach-O
            b"\xce\xfa\xed\xfe",  # Mach-O
            b"\xcf\xfa\xed\xfe",  # Mach-O 64-bit
        ]

        return any(header.startswith(exe_header) for exe_header in executable_headers)

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for security.

        Args:
            filename: Original filename
        Returns:
            str: Sanitized filename

        """
        try:
            # Remove any path components
            filename = Path(filename).name

            # Remove or replace dangerous characters
            # Allow alphanumeric, dots, hyphens, underscores
            sanitized = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

            # Prevent hidden files
            if sanitized.startswith("."):
                sanitized = "file" + sanitized

            # Prevent empty filename
            if not sanitized or sanitized == ".":
                sanitized = "unnamed_file"

            # Limit length
            if len(sanitized) > 255:
                name_part = sanitized[:200]
                ext_part = sanitized[200:]
                # Try to preserve extension
                if "." in ext_part:
                    ext = ext_part[ext_part.rfind(".") :]
                    sanitized = name_part + ext
                else:
                    sanitized = name_part

            # Ensure it has some extension
            if "." not in sanitized:
                sanitized += ".txt"

            logger.debug(f"Sanitized filename: '{filename}' -> '{sanitized}'")
            return sanitized
        except Exception as e:
            logger.error(f"Error sanitizing filename {filename}: {e}")
            return "safe_filename.txt"
