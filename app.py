# from flask import Flask, request, render_template
# import pandas as pd
# import os

# app = Flask(__name__)

# def save_to_excel(data, filename="qr_data.xlsx"):
#     if os.path.exists(filename):
#         df = pd.read_excel(filename)
#     else:
#         df = pd.DataFrame(columns=["Scanned Data"])

#     df = pd.concat([df, pd.DataFrame({"Scanned Data": [data]})], ignore_index=True)
#     df.to_excel(filename, index=False)

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/scan", methods=["POST"])
# def scan():
#     qr_data = request.form.get("qr_data")
#     save_to_excel(qr_data)
#     return "Data Saved!"

# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, request, render_template
import pandas as pd
import os
from werkzeug.utils import secure_filename
import cv2

app = Flask(__name__)

# Set the upload folder and allowed extensions for the image
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_to_excel(data, filename="qr_data.xlsx"):
    if os.path.exists(filename):
        df = pd.read_excel(filename)
    else:
        df = pd.DataFrame(columns=["Scanned Data"])

    df = pd.concat([df, pd.DataFrame({"Scanned Data": [data]})], ignore_index=True)
    df.to_excel(filename, index=False)

# Function to scan QR code from image
def scan_qr_from_image(image_path):
    # Read the uploaded image
    image = cv2.imread(image_path)
    detector = cv2.QRCodeDetector()

    # Detect QR code in the image
    data, bbox, _ = detector.detectAndDecode(image)

    if data:
        return data
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'file' not in request.files:
            return "No file part", 400

        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Process the uploaded image
            qr_data = scan_qr_from_image(file_path)
            if qr_data:
                save_to_excel(qr_data)
                return f"QR Code Data: {qr_data} has been saved to Excel."
            else:
                return "No QR Code found in the image."

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
