import google.generativeai as genai
import os
import json
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise Exception("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def extract_pan_details(image_path):

    if not os.path.exists(image_path):
        return {"error": "File not found"}

    try:
        img = Image.open(image_path)

        prompt = """
        This is an Indian PAN card image. It may be rotated, blurry or have a watermark.
        Carefully extract the following details.

        Return ONLY valid JSON with these exact keys:
        - pan_number: 10 character Permanent Account Number (format: 5 letters + 4 digits + 1 letter e.g. ABCDE1234F)
        - name: Card holder full name (in CAPITAL letters)
        - father_name: Father's full name (second name line on card)
        - date_of_birth: Date of birth in DD/MM/YYYY format

        Rules:
        - If any field is not found return null
        - Return ONLY JSON, no explanation, no markdown
        """

        response = model.generate_content([prompt, img])
        raw = response.text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        return json.loads(raw)

    except Exception as e:
        return {
            "error": "Failed to extract PAN details",
            "details": str(e)
        }