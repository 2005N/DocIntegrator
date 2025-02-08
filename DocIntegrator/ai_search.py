from flask import Blueprint, request, jsonify, render_template, current_app
from werkzeug.utils import secure_filename
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
from extract_text import process_documents

# Create a Blueprint with a unique name (ai_search_bp)
ai_search_bp = Blueprint("ai_search", __name__)

UPLOAD_FOLDER = "./downloaded_files"
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

# Load AI model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Extract text from existing documents
documents = process_documents(UPLOAD_FOLDER)

# Convert extracted text into embeddings
doc_names = list(documents.keys())
doc_embeddings = np.array([model.encode(documents[doc]) for doc in doc_names])

# Store embeddings in FAISS index
dimension = doc_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(doc_embeddings)

doc_map = {i: doc_names[i] for i in range(len(doc_names))}

def search_documents(query, top_k=5):
    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, top_k)
    results = [doc_map[idx] for idx in indices[0] if idx in doc_map]
    return results

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def update_faiss_index(documents):
    """Update FAISS index with new documents while avoiding duplicates."""
    global doc_map, index
    doc_names = list(documents.keys())

    for doc_name in doc_names:
        if doc_name in doc_map.values():  # Skip already indexed documents
            continue
        
        doc_embedding = model.encode([documents[doc_name]])
        index.add(np.array(doc_embedding))
        doc_map[len(doc_map)] = doc_name


@ai_search_bp.route("/ai_search")
def ai_search_page():
    return render_template("ai_search.html")

@ai_search_bp.route("/search", methods=["POST"])
def search():
    data = request.json
    query = data.get("query", "")

    if not query:
        return jsonify({"error": "Query is required"}), 400

    results = search_documents(query)
    return jsonify({"results": results})

@ai_search_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Use current_app.config to access configuration in a blueprint
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        # Extract text from the new document
        new_doc_text = process_documents(current_app.config["UPLOAD_FOLDER"]).get(filename, "")
        
        if new_doc_text:
            new_embedding = model.encode([new_doc_text])
            index.add(np.array(new_embedding))
            doc_map[len(doc_map)] = filename
            return jsonify({"message": f"Uploaded and indexed {filename} successfully!"})
        else:
            return jsonify({"error": "Could not extract text from file"}), 500
    else:
        return jsonify({"error": "Invalid file type"}), 400

# Remove the standalone run block so that this file is only used as a blueprint
#if __name__ == "__main__":
#    ai_search_bp.run(debug=True)
