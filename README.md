# 📄 AI-Powered Document Integrator 

An AI-powered document search tool that integrates with **Google Drive** to fetch, download, and search documents using **semantic search** (FAISS + Sentence Transformers).  

## Features
- 🔹 **Google Drive Integration**: List, upload, and download files.  
- 🔹 **AI-Powered Search**: Search document contents using semantic similarity instead of exact keywords.  
- 🔹 **Local File Management**: Index and search locally stored files.  
- 🔹 **Expandable**: Can integrate Dropbox or OneDrive in the future.  

## Tech Stack
- **Backend:** Flask (Python)  
- **AI Model:** Sentence Transformers (`all-MiniLM-L6-v2`)  
- **Vector Search:** FAISS  
- **Google Drive API** for cloud file access  
- **Frontend:** HTML, JavaScript  

Install Dependencies and Setup Google Drive API.
Go to Google Cloud Console and create a new project.
Enable the Google Drive API and download credentials.json.
Place credentials.json in the project root.