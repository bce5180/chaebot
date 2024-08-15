document.addEventListener("DOMContentLoaded", function () {
  var fileInput = document.getElementById("file-input");
  var findBtn = document.getElementById("find-btn");
  var dropZone = document.getElementById("mp3-upload-box");
  var backgroundAnimation = document.querySelector(".background-animation");
  var uploadBtn = document.getElementById("upload-btn");

  // 이미지 경로를 HTML에서 가져오기
  var imagePath = document.getElementById('file-name-display').getAttribute('data-image-url');

  function isMP3File(file) {
    return file.type === "audio/mp3" || file.name.endsWith(".mp3");
  }

  function displayFileName(fileName) {
    const neonBox = document.getElementById('file-name-display');
    if (neonBox) {
      neonBox.innerHTML = `<img src="${imagePath}" alt="Music Upload Icon" class="upload-icon"> ${fileName}`;
      neonBox.style.display = 'block';
    }
  }

  if (findBtn) {
    findBtn.addEventListener("click", function () {
      fileInput.click();
    });
  } else {
    console.log("Find button not found!");
  }

  fileInput.addEventListener("change", function () {
    if (fileInput.files.length > 0) {
      const file = fileInput.files[0];
      if (isMP3File(file)) {
        displayFileName(file.name);
      } else {
        alert("Please select an MP3 file.");
        fileInput.value = "";
      }
    }
  });

  if (dropZone) {
    dropZone.addEventListener("dragover", function (event) {
      event.preventDefault();
      dropZone.style.backgroundColor = "rgba(128,128,128,0.3)";
    });

    dropZone.addEventListener("dragleave", function (event) {
      event.preventDefault();
      dropZone.style.backgroundColor = "transparent";
    });

    dropZone.addEventListener("drop", function (event) {
      event.preventDefault();
      dropZone.style.backgroundColor = "transparent";
      const files = event.dataTransfer.files;
      if (files.length > 0) {
        const file = files[0];
        if (isMP3File(file)) {
          fileInput.files = files; // 파일을 file input에 연결
          displayFileName(file.name); // 파일명을 표시
        } else {
          alert("Please drop an MP3 file.");
        }
      }
    });
  } else {
    console.log("Drop zone element not found!");
  }

  window.addEventListener("load", () => {
    backgroundAnimation.style.clipPath = "circle(75% at 100% 50%)";
    setTimeout(() => {
      document.querySelector(".container").style.opacity = 1;
    }, 2000);
  });


  window.addEventListener("load", () => {
    backgroundAnimation.style.clipPath = "circle(75% at 100% 50%)";
    setTimeout(() => {
      document.querySelector(".container").style.opacity = 1;
    }, 2000);
  });


  function getCsrfToken() {
    return document.querySelector('input[name="csrfmiddlewaretoken"]').value;
  }

  uploadBtn.addEventListener("click", function (e) {
    e.preventDefault();
    if (fileInput.files.length > 0) {
      window.location.href = "waiting/";
      const file = fileInput.files[0];
      const formData = new FormData();
      formData.append("file", file);
      formData.append("csrfmiddlewaretoken", getCsrfToken());

      fetch("/upload/", {
        method: "POST",
        body: formData,
      })
        .then((response) => {
          if (response.ok) {
            window.location.href = "waiting/";
            return response.json();
          }
          throw new Error("Network response was not ok.");
        })
        .then((data) => {
          console.log(data);
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    } else {
      alert("Please select a file to upload.");
    }
  });
});

window.addEventListener("load", function () {
  setTimeout(function () {
    document.querySelector(".content").style.display = "block";
  }, 2000); // 2초 후에 content 보이기
});

function displayFileName(fileName) {
  const neonBox = document.getElementById('file-name-display');
  if (neonBox) {
    neonBox.innerHTML = `<img src="{% static 'img/music_upload.png' %}" class="upload-icon"> ${fileName}`;
    neonBox.style.display = 'block';
  }
}
