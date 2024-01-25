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
let startDate;
let time = 1800;
let interval;
let isRunning = false;

function setTimer() {
  const setTimeInput = document.getElementsByName("settime")[0];
  const timerEl = document.getElementById("timer");

  const timeParts = setTimeInput.value.split(':');

  // 時間を秒に変換
  const hours = parseInt(timeParts[0], 10);
  const minutes = parseInt(timeParts[1], 10);
  const seconds = parseInt(timeParts[2], 10);
  time = (hours * 3600) + (minutes * 60) + seconds;

  // タイマー表示を更新
  timerEl.innerHTML = formatTime(time);
}

function formatTime(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return [h, m, s].map(v => v < 10 ? "0" + v : v).join(":");
}

function formatDate(date) {
  var year = date.getFullYear();
  var month = String(date.getMonth() + 1).padStart(2, '0'); // 月は0から始まるため+1する
  var day = String(date.getDate()).padStart(2, '0');

  var hour = String(date.getHours()).padStart(2, '0');
  var minute = String(date.getMinutes()).padStart(2, '0');

  return year + ':' + month + ':' + day + ' ' + hour + ':' + minute;
}

function fixTimer() {
  // タイマーを確定してmemo画面に遷移
  const setTimeInput = document.getElementsByName("settime")[0];
  const timeParts = setTimeInput.value.split(':');

  // 時間を秒に変換
  const hours = parseInt(timeParts[0], 10);
  const minutes = parseInt(timeParts[1], 10);
  const seconds = parseInt(timeParts[2], 10);

  // 経過時間を秒で取得
  const execution_time = (hours * 3600) + (minutes * 60) + seconds - time;
  console.log(execution_time);

  // memoのレイアウトに反映
  startDate ??= new Date();
  document.getElementById('execution_date').innerHTML = formatDate(startDate);
  document.getElementById('execution_time').innerHTML = formatTime(execution_time);

  // レイアウトを切り替え
  toggleLayout();
}

function resetTimer() {
  const timerEl = document.getElementById("timer");
  clearInterval(interval);
  timerEl.style = "";
  
  timerEl.innerHTML = "00:00:00"; // タイマー表示をリセット
  time = 0; // time変数をリセット
  startDate = null; // startDate変数をリセット

  const StartBtnEl = document.getElementById("start-btn");
  StartBtnEl.innerHTML = "START";
  StartBtnEl.style = "";

  const doneBtnEl = document.getElementById("done-btn");
  doneBtnEl.classList.remove("disabled");
}

function stopTimer() {
  const StartBtnEl = document.getElementById("start-btn");

  StartBtnEl.innerHTML = "START";
  StartBtnEl.style = "";

  const timerEl = document.getElementById("timer");
  clearInterval(interval);
  timerEl.style = "";

  const doneBtnEl = document.getElementById("done-btn");
  doneBtnEl.classList.remove("disabled");
}

function startTimer() {
  startDate ??= new Date(); // 1度だけ
  isRunning = !isRunning
  
  const timerEl = document.getElementById("timer"); // タイマー表示用の要素を取得
  clearInterval(interval);
  timerEl.style = "";

  const StartBtnEl = document.getElementById("start-btn");
  const doneBtnEl = document.getElementById("done-btn");
  
  if (!isRunning) {
    stopTimer();
    return;
  }
  
  doneBtnEl.classList.add("disabled");
  StartBtnEl.innerHTML = "STOP";
  StartBtnEl.style = "color: red"

  interval = setInterval(() => {
    if (time <= 0) {
      clearInterval(interval);
      timerEl.style = "color: red";
      fixTimer();
    } else {
      time--;
      timerEl.innerHTML = formatTime(time)
    }
  }, 1000);
}

document.getElementById('progressSlider').addEventListener('input', function() {
  var value = this.value;
  document.getElementById('progressSliderLabel').innerText = value + '%';
});

document.getElementById('start-btn').addEventListener('click', startTimer);
document.getElementById('reset-btn').addEventListener('click', resetTimer);
document.getElementById('done-btn').addEventListener('click', fixTimer);

document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('review_task').addEventListener('submit', function(event) {
    event.preventDefault(); // デフォルトの送信動作を防止
    // タイマーが実行中であれば一時停止
    if (isRunning) {
      isRunning = !isRunning;
      stopTimer();
    }
    // タイマーを確定
    const setTimeInput = document.getElementsByName("settime")[0];
    const timeParts = setTimeInput.value.split(':');

    // 時間を秒に変換
    const hours = parseInt(timeParts[0], 10);
    const minutes = parseInt(timeParts[1], 10);
    const seconds = parseInt(timeParts[2], 10);

    // 経過時間を秒で取得
    const execution_time = (hours * 3600) + (minutes * 60) + seconds - time;

    // memoのレイアウトに反映
    startDate ??= new Date();
    document.getElementById('execution_date').innerHTML = formatDate(startDate);
    document.getElementById('execution_time').innerHTML = formatTime(execution_time);

    const formData = new FormData(this); // フォームのデータを収集
    formData.append('task_id', 1);
    formData.append('execution_date', startDate.toISOString());
    formData.append('execution_time', execution_time);

    const formDataObj = Object.fromEntries(formData.entries());
    // Flask側にデータを送信するPOSTリクエストを行う
    fetch('/task_execution', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify(formDataObj),
    })
    .then(response => response.json())
    .then(data => {
      // レスポンスを処理する（必要に応じて）
      console.log(data);
    })
    .catch(error => {
      console.error('データの送信エラー:', error);
    });

    resetTimer();
  });
});

document.addEventListener("DOMContentLoaded", function() {
  // URLからクエリパラメータを取得
  const params = new URLSearchParams(window.location.search);

  // 'query'という名前のクエリパラメータの値を取得
  const queryValue = params.get('task_name');

  // input要素に値を設定
  if (queryValue) {
    document.getElementById('task_name').value = queryValue;
  }
});