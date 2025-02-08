from flask import Flask, request, jsonify, render_template
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import os
import io
from extract_text import process_documents
from ai_search import update_faiss_index, ai_search_bp

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "./downloaded_files"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Register the AI search blueprint
app.register_blueprint(ai_search_bp)

SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_drive():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)

@app.route("/")
def home():
    return render_template("drive_connector.html")

@app.route("/list_files", methods=["GET"])
def list_drive_files():
    try:
        service = authenticate_drive()
        results = service.files().list(pageSize=20, fields="files(id, name)").execute()
        files = results.get("files", [])
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/download_file", methods=["POST"])
def download_file():
    try:
        service = authenticate_drive()
        data = request.get_json() 
        file_id = data.get("file_id")
        file_name = data.get("file_name")

        if not file_id or not file_name:
            return jsonify({"error": "File ID and name are required"}), 400

        drive_request = service.files().get_media(fileId=file_id)  
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, drive_request)
        done = False

        while not done:
            status, done = downloader.next_chunk()

        fh.seek(0)
        with open(os.path.join(app.config["UPLOAD_FOLDER"], file_name), "wb") as f:
            f.write(fh.read())

        # Update AI search index with the newly downloaded file
        documents = process_documents(app.config["UPLOAD_FOLDER"])
        update_faiss_index(documents)

        return jsonify({"message": f"Downloaded {file_name} successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/upload_file", methods=["POST"])
def upload_file_drive():
    try:
        service = authenticate_drive()
        file = request.files["file"]

        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        file_metadata = {"name": file.filename}
        media = MediaFileUpload(file_path, resumable=True)
        uploaded_file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

        return jsonify({"message": f"Uploaded {file.filename} with ID: {uploaded_file['id']}"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/ai_search")
def ai_search_page():
    return render_template("ai_search.html") 

if __name__ == "__main__":
    app.run(debug=True)
