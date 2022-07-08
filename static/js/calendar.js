// Render a calendar
function draw_calendar(data, trip_start){
    var calendarEl = document.getElementById('calendar');

    var calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'dayGridMonth',
      initialDate: trip_start,
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay'
      },
      events: data,
      eventColor: '#4ad0f9',
    });

    calendar.render();
}

fetch(`/send_calendar_data/${window.location.href.split("/")[4]}`)
.then((response) => response.json())
.then((data) => {
  const calendar_data = data;
  draw_calendar(calendar_data.activities, calendar_data.trip_start);
})

