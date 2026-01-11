(function () {
    // Prevent multiple bindings if script is loaded twice accidentally
    if (window.__eventLikeBound) return;
    window.__eventLikeBound = true;

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

    document.addEventListener("submit", function (e) {
        const form = e.target.closest(".like-form");
        if (!form) return;

        // 🚫 Stop normal form submission (this prevents page refresh)
        e.preventDefault();

        // Safety: prevent double-click spam
        if (form.dataset.loading === "true") return;
        form.dataset.loading = "true";

        const icon = form.querySelector("i");
        const count = form.querySelector(".like-count");

        fetch(form.action, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(res => {
            if (!res.ok) throw new Error("Like request failed");
            return res.json();
        })
        .then(data => {
            if (data.liked) {
                icon.classList.remove("far", "text-secondary");
                icon.classList.add("fas", "text-danger");
            } else {
                icon.classList.remove("fas", "text-danger");
                icon.classList.add("far", "text-secondary");
            }
            count.textContent = data.likes_count;
        })
        .catch(err => console.error(err))
        .finally(() => {
            form.dataset.loading = "false";
        });
    });
})();
