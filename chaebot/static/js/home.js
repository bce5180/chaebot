function uploadFiles() {
  const fileInput = document.getElementById("fileInput");
  const files = fileInput.files;
  if (files.length > 0) {
    document.getElementById("convertBtn").disabled = false;
  }
}

document.getElementById("fileInput").addEventListener("change", uploadFiles);
