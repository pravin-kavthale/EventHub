
console.log("Participants JS loaded");
function loadParticipants(url) {
    const body = document.getElementById("participantsBody");

    body.innerHTML = "<p class='text-muted'>Loading...</p>";

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not OK");
            }
            return response.json();
        })
        .then(data => {
            if (data.length === 0) {
                body.innerHTML = "<p>No participants yet.</p>";
                return;
            }

            body.innerHTML = "";

            data.forEach(user => {
                body.innerHTML += `
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <a href="/Events/profile/${user.username}/" class="fw-bold" style="color:black">
                            ${user.username}
                        </a>
                        <span class="text-muted">${user.email}</span>
                    </div>
                `;
            });
        })
        .catch(error => {
            console.error(error);
            body.innerHTML = "<p class='text-danger'>Failed to load participants.</p>";
        });
}
