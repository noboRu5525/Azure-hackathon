// global variables
let time = 0;
let interval;
let flag = true;

function setTimer() {
  const setTimeInput = document.getElementsByName("settime")[0];
  const timerElement = document.getElementById("timer");

  timerElement.innerHTML = setTimeInput.value
  time = setTimeInput.value;
  const timeParts = setTimeInput.value.split(':');

  // 時間を秒に変換
  const hours = parseInt(timeParts[0], 10);
  const minutes = parseInt(timeParts[1], 10);
  const seconds = parseInt(timeParts[2], 10);
  time = (hours * 3600) + (minutes * 60) + seconds;

  // タイマー表示を更新
  timerElement.innerHTML = formatTime(time);
}

function formatTime(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return [h, m, s].map(v => v < 10 ? "0" + v : v).join(":");
}

function resetTimer() {
  const timerElement = document.getElementById("timer");
  clearInterval(interval);
  timerElement.style = "";
  
  timerElement.innerHTML = "00:00:00"; // タイマー表示をリセット
  time = 0; // time変数をリセット
}

function stopTimer() {
  const timerElement = document.getElementById("timer");
  clearInterval(interval);
  timerElement.style = "";
}

function startTimer() {
  flag = !flag
  
  const timerElement = document.getElementById("timer"); // タイマー表示用の要素を取得
  clearInterval(interval);
  timerElement.style = "";

  const btnElm = document.getElementById("start-btn");

  if (flag) {
    btnElm.innerHTML = "START";
    return;
  }

  btnElm.innerHTML = "STOP";

  interval = setInterval(() => {
    if (time <= 0) {
      clearInterval(interval);
      timerElement.style = "color: red";
    } else {
      time--;
      timerElement.innerHTML = formatTime(time)
    }
  }, 1000);
}

