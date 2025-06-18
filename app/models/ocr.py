import base64
import io
import pytesseract

from PIL import Image

class OCR:
    def __init__(self):
        pass

    def extract_text(self, image_data: str) -> str:
        try:
            img = Image.open(io.BytesIO(base64.b64decode(image_data)))
            return pytesseract.image_to_string(img)
        except Exception as e:
            raise ValueError(f"OCR decoding error: {e}")