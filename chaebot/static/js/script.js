document.addEventListener("DOMContentLoaded", function () {
  var fileInput = document.getElementById("file-input");
  var findBtn = document.getElementById("find-btn");
  var uploadBtn = document.getElementById("upload-btn");
  var dropZone = document.getElementById("drop-zone");

  // 파일 입력 창을 여는 'Find' 버튼
  if (findBtn) {
    findBtn.addEventListener("click", function () {
      fileInput.click();
    });
  } else {
    console.log("Find button not found!");
  }

  // 'Upload' 버튼 이벤트
  if (uploadBtn) {
    uploadBtn.addEventListener("click", function () {
      const file = fileInput.files[0];
      if (file) {
        console.log("Uploading:", file.name);
        // Upload logic here
      } else {
        alert("Please select a file to upload.");
      }
    });
  } else {
    console.log("Upload button not found!");
  }

  // 드래그 앤 드롭 이벤트
  if (dropZone) {
    dropZone.addEventListener("click", function () {
      fileInput.click();
    });

    dropZone.addEventListener("dragover", function (event) {
      event.preventDefault();
      dropZone.style.backgroundColor = "rgba(128,128,128,0.3)";
    });

    dropZone.addEventListener("dragleave", function (event) {
      dropZone.style.backgroundColor = "rgba(0,0,0,0.5)";
    });

    dropZone.addEventListener("drop", function (event) {
      event.preventDefault();
      dropZone.style.backgroundColor = "rgba(0,0,0,0.5)";
      const files = event.dataTransfer.files;
      fileInput.files = files;
      console.log("File uploaded:", files[0].name);
    });
  } else {
    console.log("Drop zone element not found!");
  }

  // 페이지 로드 시 애니메이션 효과
  document.querySelector(".background-animation").style.clipPath =
    "circle(75% at 100% 50%)";
  setTimeout(() => {
    document.querySelector(".container").style.opacity = 1;
  }, 2000);
});

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

document.addEventListener("DOMContentLoaded", function () {
  var fileInput = document.getElementById("file-input");
  var findBtn = document.getElementById("find-btn");

  if (findBtn) {
    findBtn.addEventListener("click", function () {
      fileInput.click(); // 파일 입력을 트리거합니다.
    });
  } else {
    console.log("Find button not found!");
  }

  // 기타 드래그 앤 드롭 관련 이벤트는 생략합니다.
  // 이 부분은 당신의 요구에 따라 조정하세요.
});
