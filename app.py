"""Command-line entry point for image validation."""

import argparse

from image_service import validate_image
from ai_service import request_ai_response


_IMAGE_ANALYSIS_PROMPT = "Analyze this payment proof image and describe the payment details you can read."


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a local payment proof image.")
    parser.add_argument("image_path", help="Path to a PNG, JPG, JPEG, or WEBP image")
    args = parser.parse_args()

    result = validate_image(args.image_path)
    label = "Success" if result.valid else "Error"
    print(f"{label}: {result.message}")
    if not result.valid:
        return 1

    try:
        response = request_ai_response(_IMAGE_ANALYSIS_PROMPT, image_path=args.image_path)
    except RuntimeError as exc:
        print(f"AI error: {exc}")
        return 1
    print(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
