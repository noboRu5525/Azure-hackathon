

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
