import google.generativeai as genai
import os
from dotenv import load_dotenv
import PyPDF2
import docx
import json
from PIL import Image

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise Exception("GEMINI_API_KEY not found")

genai.configure(api_key=API_KEY)

# Move model to module level — instantiated once, reused on every request
model = genai.GenerativeModel("gemini-2.5-flash")


def extract_text_from_file(file_path):
    text = ""
    # Fix: use os.path.splitext for reliable extension parsing
    extension = os.path.splitext(file_path)[1].lower().lstrip('.')

    if extension == "pdf":
        try:
            reader = PyPDF2.PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""

    elif extension == "docx":
        try:
            doc = docx.Document(file_path)
            text = "\n".join(p.text for p in doc.paragraphs)
        except Exception as e:
            print(f"Error reading DOCX: {e}")
            return ""

    return text.strip()


def parse_resume(file_path):

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    # Fix: use os.path.splitext for reliable extension parsing
    extension = os.path.splitext(file_path)[1].lower().lstrip('.')

    prompt = f"""
    You are a resume parser. Extract ALL required data fields from the document provided, which is a resume.

    Return ONLY valid JSON.
    Always return ALL keys listed below.
    If a value is not found, return null (for string fields) or an empty array [] (for list fields).
    Do not skip any key.

    Keys:
    - full_name
    - email
    - phone
    - skills
    - experience
    - education
    - summary
    - technologies
    - years_of_experience
    """

    model_input = [prompt]

    if extension in ["pdf", "docx"]:
        text = extract_text_from_file(file_path)
        if not text or len(text) < 50:
            return {"error": "No readable text found in document"}

        # Increased limit — Gemini 2.5 Flash supports large context
        model_input.append(f"Resume Text to parse:\n{text[:30000]}")

    elif extension in ["jpg", "jpeg", "png"]:
        try:
            img = Image.open(file_path)
            model_input.append(img)
        except Exception as e:
            return {"error": "Failed to open image file", "details": str(e)}

    else:
        return {"error": f"Unsupported file type: {extension}. Supported: PDF, DOCX, JPG, JPEG, PNG"}

    try:
        response = model.generate_content(model_input)

        raw = response.text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        return json.loads(raw)

    except Exception as e:
        return {
            "error": "Gemini parsing failed",
            "details": str(e)
        }