document.addEventListener("DOMContentLoaded", function () {
  var fileInput = document.getElementById("file-input");
  var findBtn = document.getElementById("find-btn");
  var dropZone = document.getElementById("drop-zone");
  var backgroundAnimation = document.querySelector(".background-animation");
  var loadingOverlay = document.getElementById("loading-overlay");
  var uploadBtn = document.getElementById("upload-btn");
  var counterElement = document.getElementById("conversion-counter");
  // Django 템플릿 변수로부터 변환 수를 받아올 경우 서버에서 해당 값을 주입해야 합니다.
  // 예: var finalCount = {{ conversion_count }};
  var finalCount = 100; // 임시 값
  let currentCount = 0;
  const countElement = document.getElementById("conversion-count");
  const targetCount = 924; // 최종 변환수, 서버로부터 받아올 수도 있음

  function isMP3File(file) {
    return file.type === "audio/mp3" || file.name.endsWith(".mp3");
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
      dropZone.style.backgroundColor = "rgba(0,0,0,0.5)";
    });

    dropZone.addEventListener("drop", function (event) {
      event.preventDefault();
      dropZone.style.backgroundColor = "rgba(0,0,0,0.5)";
      const files = event.dataTransfer.files;
      if (files.length > 0) {
        const file = files[0];
        if (isMP3File(file)) {
          fileInput.files = files;
          displayFileName(file.name);
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
