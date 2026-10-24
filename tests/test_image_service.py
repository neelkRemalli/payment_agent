from PIL import Image

from image_service import MAX_IMAGE_SIZE_BYTES, validate_image


def make_image(path):
    Image.new("RGB", (3, 2), color="navy").save(path)
    return path


def test_valid_synthetic_image_is_accepted(tmp_path):
    path = make_image(tmp_path / "proof.png")

    result = validate_image(path)

    assert result.valid is True
    assert "Valid image" in result.message


def test_missing_file_is_rejected(tmp_path):
    result = validate_image(tmp_path / "missing.png")

    assert result.valid is False
    assert "does not exist" in result.message


def test_directory_is_rejected(tmp_path):
    result = validate_image(tmp_path)

    assert result.valid is False
    assert "not a regular file" in result.message


def test_unsupported_extension_is_rejected(tmp_path):
    path = tmp_path / "proof.gif"
    Image.new("RGB", (1, 1)).save(path, format="PNG")

    result = validate_image(path)

    assert result.valid is False
    assert "Unsupported" in result.message


def test_empty_file_is_rejected(tmp_path):
    path = tmp_path / "proof.jpg"
    path.touch()

    result = validate_image(path)

    assert result.valid is False
    assert "empty" in result.message


def test_file_larger_than_limit_is_rejected(tmp_path):
    path = tmp_path / "large.webp"
    with path.open("wb") as image_file:
        image_file.truncate(MAX_IMAGE_SIZE_BYTES + 1)

    result = validate_image(path)

    assert result.valid is False
    assert "larger than 10 MB" in result.message


def test_corrupt_image_content_is_rejected(tmp_path):
    path = tmp_path / "corrupt.png"
    path.write_bytes(b"not an image")

    result = validate_image(path)

    assert result.valid is False
    assert "not a valid, decodable image" in result.message
