document.addEventListener('DOMContentLoaded', function() {
    const reportButtons = document.querySelectorAll('.report-btn');

    reportButtons.forEach(button => {
        button.addEventListener('click', function() {
            const form = button.closest('.report-form');
            const eventId = form.dataset.eventId;
            const reason = button.value;
            const csrftoken = form.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(`/Events/events/${eventId}/report/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `reason=${encodeURIComponent(reason)}`
            })
            .then(response => response.json())
            .then(data => {
                const msgDiv = document.getElementById(`report-message-${eventId}`);
                if (data.status === 'success') {
                    msgDiv.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                } else {
                    msgDiv.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});
