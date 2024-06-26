document.addEventListener("DOMContentLoaded", function () {
  setTimeout(function () {
    document.getElementById("welcome-box").style.display = "block"; // 네온 박스 표시
    document
      .querySelectorAll(".note")
      .forEach((el) => (el.style.display = "block")); // 음표 표시
  }, 2100); // 선이 확장되고 바로 음표와 네온 박스를 표시
});
