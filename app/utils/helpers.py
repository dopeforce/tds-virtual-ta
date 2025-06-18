import io
import json
import base64
import pytesseract
import numpy as np

from PIL import Image
from typing import Any, Dict, List

def load_json(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file_path: str, data: Dict[str, Any]) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def extract_text_from_image(image_data: str) -> str:
    img = Image.open(io.BytesIO(base64.b64decode(image_data)))
    return pytesseract.image_to_string(img)

def handle_ocr(image_data: str) -> str:
    try:
        return extract_text_from_image(image_data)
    except Exception as e:
        raise ValueError(f"OCR decoding error: {e}")