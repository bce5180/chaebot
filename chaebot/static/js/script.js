document.addEventListener("DOMContentLoaded", function () {
  var fileInput = document.getElementById("file-input");
  var findBtn = document.getElementById("find-btn");
  var dropZone = document.getElementById("drop-zone"); // drop-zone 사용으로 통일
  var backgroundAnimation = document.querySelector(".background-animation");

  // 파일 이름을 표시하고 drop-zone을 숨기는 함수
  function displayFileName(fileName) {
    dropZone.style.display = "none"; // drop-zone 숨기기
    var fileNameDisplay = document.createElement("div");
    fileNameDisplay.textContent = fileName;
    fileNameDisplay.style.color = "black";
    fileNameDisplay.style.fontWeight = "bold";
    fileNameDisplay.style.textAlign = "center";
    fileNameDisplay.style.fontSize = "20px";
    dropZone.parentNode.insertBefore(fileNameDisplay, dropZone.nextSibling);
  }

  // Find 버튼 이벤트 핸들러
  if (findBtn) {
    findBtn.addEventListener("click", function () {
      fileInput.click();
    });
  } else {
    console.log("Find button not found!");
  }

  // 파일 선택 변경 시 파일 이름 표시
  fileInput.addEventListener("change", function () {
    if (fileInput.files.length > 0) {
      displayFileName(fileInput.files[0].name);
    }
  });

  // 드래그 앤 드롭 이벤트
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
        fileInput.files = files; // 파일 입력을 수동으로 설정
        displayFileName(files[0].name);
      }
    });
  } else {
    console.log("Drop zone element not found!");
  }

  // 페이지 로드 완료 후 애니메이션 실행
  window.addEventListener("load", () => {
    backgroundAnimation.style.clipPath = "circle(75% at 100% 50%)";
    setTimeout(() => {
      document.querySelector(".container").style.opacity = 1;
    }, 2000);
  });
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
