function uploadFile() {
    let fileInput = document.getElementById("fileInput").files[0];
    if (!fileInput) {
        alert("Please select a file to upload.");
        return;
    }

    let formData = new FormData();
    formData.append("file", fileInput);

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("uploadStatus").innerText = data.message;
    })
    .catch(error => console.error("Error:", error));
}

function searchDocuments() {
    let query = document.getElementById("searchQuery").value;
    if (!query) {
        alert("Please enter a search query.");
        return;
    }

    fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        let resultsList = document.getElementById("results");
        resultsList.innerHTML = "";
        data.results.forEach(doc => {
            let li = document.createElement("li");
            li.textContent = doc;
            resultsList.appendChild(li);
        });
    })
    .catch(error => console.error("Error:", error));
}