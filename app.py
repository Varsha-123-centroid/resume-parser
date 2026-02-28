from flask import Flask, request, jsonify
from extractor import parse_resume
from pan_extractor import extract_pan_details
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Max file size: 5MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "docx", "jpg", "jpeg", "png"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/parse", methods=["POST"])
def parse():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Validate file type BEFORE saving
    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type. Allowed: PDF, DOCX, JPG, JPEG, PNG"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        file.save(file_path)

        parsed_data = parse_resume(file_path)

        if "error" in parsed_data:
            return jsonify(parsed_data), 500

        return jsonify(parsed_data)

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred during processing", "details": str(e)}), 500

    finally:
        # Always clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.route("/parse-pan", methods=["POST"])
def parse_pan():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type. Allowed: JPG, JPEG, PNG"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        file.save(file_path)
        result = extract_pan_details(file_path)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.route("/view")
def view_parsed_resume():
    file_path = os.path.join(UPLOAD_FOLDER, "sample.pdf")

    if not os.path.exists(file_path):
        return "No sample.pdf found in uploads folder", 404

    parsed_data = parse_resume(file_path)

    # Fix: render as proper JSON string, not raw dict
    html_output = "<h2>Parsed Resume Data</h2><pre>{}</pre>".format(json.dumps(parsed_data, indent=2))

    return html_output


@app.route("/")
def home():
    return "Resume Parser API with Gemini is running"


if __name__ == "__main__":
    # Use environment variable to control debug mode
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, port=5001)