(function () {
    if (window.__eventJoinBound) return;
    window.__eventJoinBound = true;

    function getCookie(name) {
        let value = null;
        if (document.cookie) {
            document.cookie.split(";").forEach(c => {
                c = c.trim();
                if (c.startsWith(name + "=")) {
                    value = decodeURIComponent(c.substring(name.length + 1));
                }
            });
        }
        return value;
    }

    document.addEventListener("click", function (e) {
        const btn = e.target.closest(".join-btn");
        if (!btn) return;

        // 🚫 prevent double clicks + duplicate fetches
        if (btn.dataset.loading === "true") return;
        btn.dataset.loading = "true";
        btn.disabled = true;

        fetch(btn.dataset.url, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(res => {
            if (!res.ok) throw new Error("Join request failed");
            return res.json();
        })
        .then(data => {
            if (data.joined) {
                btn.textContent = "Leave";
                btn.classList.remove("btn-success");
                btn.classList.add("btn-danger");
            } else {
                btn.textContent = "Join";
                btn.classList.remove("btn-danger");
                btn.classList.add("btn-success");
            }
        })
        .catch(err => {
            console.error(err);
        })
        .finally(() => {
            btn.dataset.loading = "false";
            btn.disabled = false;
        });
    });
})();
