let isTimer = true;

function toggleLayout() {
  document.getElementById('timer-container').classList.toggle("d-none");
  document.getElementById('memo-container').classList.toggle("d-none");
  document.getElementById('toggle-timer').classList.toggle("bg-warning");
  document.getElementById('toggle-memo').classList.toggle("bg-warning");
  isTimer = !isTimer;
}

document.getElementById('toggle-timer').addEventListener('click', function() {
  if (!isTimer) {
    toggleLayout();
  }
});
document.getElementById('toggle-memo').addEventListener('click', function() {
  if (isTimer) {
    toggleLayout();
  }
});

// global variables
let time = 0;
let interval;
let isRunning = true;

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

  const btnElm = document.getElementById("start-btn");
  btnElm.innerHTML = "START";
  btnElm.style = "";
}

function stopTimer() {
  const timerElement = document.getElementById("timer");
  clearInterval(interval);
  timerElement.style = "";
}

function startTimer() {
  isRunning = !isRunning
  
  const timerElement = document.getElementById("timer"); // タイマー表示用の要素を取得
  clearInterval(interval);
  timerElement.style = "";

  const btnElm = document.getElementById("start-btn");

  if (isRunning) {
    btnElm.innerHTML = "START";
    btnElm.style = "";
    return;
  }

  btnElm.innerHTML = "STOP";
  btnElm.style = "color: red"

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

document.getElementById('start-btn').addEventListener('click', startTimer);
document.getElementById('reset-btn').addEventListener('click', resetTimer);
document.getElementById('stop-btn').addEventListener('click', () => {
  // タイマーが実行中であれば一時停止して終了
  if (isRunning) {
    btnElm.innerHTML = "START";
    btnElm.style = "";
    return;
  }

  // 計測されたデータを取得
  const elapsedTime = Date.now() - startTime;
  const formattedTime = formatTime(elapsedTime);

  // プログレスバーの値を取得
  const progressValue = parseInt(document.getElementById('progressSlider').value);

  // コンソールに表示
  console.log('経過時間:', formattedTime);
  console.log('進捗バーの値:', progressValue);

  // データをオブジェクトにまとめる
  const dataToSend = {
      formattedTime: formattedTime,
      progressValue: progressValue,
      user_memo: "Hello. I'm happy.",
  };

  // Flask側にデータを送信するPOSTリクエストを行う
  fetch('/save_data', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify(dataToSend)
  })
  .then(response => response.json())
  .then(data => {
      // レスポンスを処理する（必要に応じて）
      console.log(data);
  })
  .catch(error => {
      console.error('データの送信エラー:', error);
  });

  // タイマーをリセット
  resetTimer();
});
