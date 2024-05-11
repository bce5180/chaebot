document.getElementById("drop-zone").addEventListener("click", function () {
  document.getElementById("file-input").click();
});

document
  .getElementById("drop-zone")
  .addEventListener("dragover", function (event) {
    event.preventDefault();
    event.target.style.backgroundColor = "rgba(128,128,128,0.3)";
  });

document
  .getElementById("drop-zone")
  .addEventListener("dragleave", function (event) {
    event.target.style.backgroundColor = "rgba(0,0,0,0.5)";
  });

document.getElementById("drop-zone").addEventListener("drop", function (event) {
  event.preventDefault();
  event.target.style.backgroundColor = "rgba(0,0,0,0.5)";
  const files = event.dataTransfer.files;
  document.getElementById("file-input").files = files;
  console.log("File uploaded:", files[0].name);
});

document.getElementById("upload-btn").addEventListener("click", function () {
  const file = document.getElementById("file-input").files[0];
  if (file) {
    console.log("Uploading:", file.name);
    // Upload logic here
  } else {
    alert("Please select a file to upload.");
  }
});
