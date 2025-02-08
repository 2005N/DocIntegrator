function listFiles() {
    fetch("/list_files")
    .then(response => response.json())
    .then(data => {
        let fileList = document.getElementById("fileList");
        fileList.innerHTML = "";
        data.files.forEach(file => {
            let li = document.createElement("li");
            li.innerHTML = `${file.name} (ID: ${file.id}) 
                <a href="#" onclick="downloadFile('${file.id}', '${file.name}')">[Download]</a>`;
            fileList.appendChild(li);
        });
    })
    .catch(error => console.error("Error:", error));
}

function downloadFile(fileId, fileName) {
    fetch("/download_file", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_id: fileId, file_name: fileName })
    })
    .then(response => response.json())
    .then(data => {
        let statusMsg = data.message || data.error;
        document.getElementById("downloadStatus").innerText = statusMsg;

        if (data.message) {
            alert("✅ " + statusMsg); // Show popup confirmation
        }
    })
    .catch(error => console.error("Error:", error));
}

function uploadFile() {
    let fileInput = document.getElementById("uploadInput").files[0];

    if (!fileInput) {
        alert("Please select a file to upload.");
        return;
    }

    let formData = new FormData();
    formData.append("file", fileInput);

    fetch("/upload_file", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("uploadStatus").innerText = data.message || data.error;
    })
    .catch(error => console.error("Error:", error));
}
