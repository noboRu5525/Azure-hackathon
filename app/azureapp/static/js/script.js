$(document).ready(function () {
    $('#sidebarCollapse').on('click', function () {
        // サイドバーの状態をトグル
        $('#sidebar').toggleClass('active');

        // メインコンテンツの位置や幅を調整
        if ($('#sidebar').hasClass('active')) {
            $('.main').css({
                'margin-left': '0' // ここでサイドバーがアクティブな時のメインコンテンツのスタイルを設定
            });
        } else {
            $('.main').css({
                'margin-left': '250px' // サイドバーが非アクティブな時のメインコンテンツのスタイルを設定
            });
        }
    });
});

//プロジェクトをカレンダーに表示
document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',

        // プロジェクトとGoogleカレンダーのイベントを取得
        events: function(fetchInfo, successCallback, failureCallback) {
            // プロジェクトのイベントを取得
            fetch('/get_projects')
                .then(response => response.json())
                .then(projectData => {
                    var projectEvents = projectData.map(project => {
                        return {
                            id: project.id,
                            title: project.title,
                            start: project.start,
                            end: project.end,
                            allDay: project.allDay,
                            backgroundColor: project.color, // 背景色を設定
                            borderColor: project.color // 枠線の色も同様に設定
                        };
                    });

                    // Googleカレンダーのイベントを取得
                    fetch('/get-calendar-events')
                        .then(response => response.json())
                        .then(calendarData => {
                            // プロジェクトのイベントとGoogleカレンダーのイベントを統合
                            var events = projectEvents.concat(calendarData);
                            successCallback(events);
                        });
                })
                .catch(error => {
                    console.error('Error:', error);
                    failureCallback(error);
                });
        }
    });

    calendar.render();
});
