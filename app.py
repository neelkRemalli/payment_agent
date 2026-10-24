"""Command-line entry point for image validation."""

import argparse

from image_service import validate_image


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a local payment proof image.")
    parser.add_argument("image_path", help="Path to a PNG, JPG, JPEG, or WEBP image")
    args = parser.parse_args()

    result = validate_image(args.image_path)
    label = "Success" if result.valid else "Error"
    print(f"{label}: {result.message}")
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
