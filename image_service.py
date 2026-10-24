"""Validation for local image files used as payment proof input."""

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError


MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


@dataclass(frozen=True)
class ImageValidationResult:
    """Outcome of validating one image path."""

    valid: bool
    message: str


def validate_image(path: str | Path) -> ImageValidationResult:
    """Check that *path* is a supported, non-empty, decodable image."""

    try:
        image_path = Path(path)
    except (TypeError, ValueError, OSError):
        return ImageValidationResult(False, "Invalid image path.")

    if not image_path.exists():
        return ImageValidationResult(False, f"File does not exist: {image_path}")
    if not image_path.is_file():
        return ImageValidationResult(False, f"Path is not a regular file: {image_path}")

    extension = image_path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        return ImageValidationResult(
            False,
            "Unsupported image format. Use PNG, JPG, JPEG, or WEBP.",
        )

    try:
        size = image_path.stat().st_size
    except OSError:
        return ImageValidationResult(False, f"Could not read file information: {image_path}")

    if size == 0:
        return ImageValidationResult(False, "Image file is empty.")
    if size > MAX_IMAGE_SIZE_BYTES:
        return ImageValidationResult(False, "Image file is larger than 10 MB.")

    try:
        # verify() checks file structure; load() decodes the pixel data as well.
        with Image.open(image_path) as image:
            image.verify()
        with Image.open(image_path) as image:
            image.load()
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError, Image.DecompressionBombError):
        return ImageValidationResult(False, "File content is not a valid, decodable image.")

    return ImageValidationResult(True, f"Valid image: {image_path}")
