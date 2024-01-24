

document.addEventListener('DOMContentLoaded', function() {
    // FullCalendar initialization
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        initialDate: '2023-11-07',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: [
            // ... Your event data here ...
        ]
    });
    calendar.render();
});
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
        events: function(fetchInfo, successCallback, failureCallback) {
            Promise.all([
                fetch('/get_projects').then(response => response.json()),
                fetch('/get_google_calendar_events').then(response => response.json())
            ])
            .then(([projectsData, googleEventsData]) => {
                var projectEvents = projectsData.map(project => ({
                    id: project.id,
                    title: project.title,
                    start: project.start,
                    end: project.end,
                    allDay: project.allDay,
                    backgroundColor: project.color,
                    borderColor: project.color
                }));

                var googleCalendarEvents = googleEventsData.map(event => ({
                    id: event.id,
                    title: event.summary,
                    start: event.start.date || event.start.dateTime,
                    end: event.end.date || event.end.dateTime,
                    allDay: !event.start.dateTime,
                    backgroundColor: '#ff9f89', // Googleカレンダーイベントの背景色
                    borderColor: '#ff9f89' // Googleカレンダーイベントの枠線色
                }));

                successCallback([...projectEvents, ...googleCalendarEvents]);
            })
            .catch(error => {
                console.error('Error:', error);
                failureCallback(error);
            });
        }
    });
    calendar.render();
});